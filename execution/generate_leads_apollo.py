#!/usr/bin/env python3
"""
Layer 3: Execution Script
Apollo.io Lead Generation Service
"""

import os
import time
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from smartsuite_client import SmartSuiteClient

# Load environment variables
load_dotenv()

class ApolloExecutionError(Exception):
    """Custom exception for Apollo API errors."""
    pass

class ApolloClient:
    BASE_URL = "https://api.apollo.io/v1"

    def __init__(self, api_key: str):
        if not api_key:
            raise ApolloExecutionError("APOLLO_API_KEY is missing")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }

    def search_people(self, job_titles: List[str], locations: List[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for people on Apollo.io with built-in retry logic for rate limits.
        """
        # Try contacts search which might have different plan requirements
        endpoint = f"{self.BASE_URL}/contacts/search"
        
        # Refined payload for Apollo API v1
        # Added q_keywords for better niche targeting (like 'plumbing')
        data = {
            "q_titles": job_titles,
            "q_keywords": "plumbing",
            "page": 1,
            "per_page": limit
        }
        
        if locations and len(locations) > 0:
            data["q_organization_locations"] = locations

        try:
            print(f"DEBUG: Trying endpoint: {endpoint}")
            response = requests.post(endpoint, json=data, headers=self.headers)
            
            # If 403, try the standard people/search as a last resort (already failed but good to have)
            if response.status_code == 403:
                print(f"DEBUG: {endpoint} failed with 403. Trying /people/search fallback...")
                endpoint = f"{self.BASE_URL}/people/search"
                data = {
                    "person_titles": job_titles,
                    "page": 1,
                    "per_page": limit
                }
                if locations: data["person_locations"] = locations
                response = requests.post(endpoint, json=data, headers=self.headers)

            response.raise_for_status()
            # Contacts API returns data in 'contacts' key, People API in 'people' key
            return response.json().get("contacts") or response.json().get("people", [])
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                raise ApolloExecutionError(f"Apollo API request failed: {e.response.status_code} - {e.response.text}")
            raise ApolloExecutionError(f"Apollo API request failed: {str(e)}")

def run_workflow(target_titles: List[str], target_locations: List[str] = None, limit: int = 5):
    """
    Main execution workflow for lead generation.
    """
    apollo_key = os.getenv("APOLLO_API_KEY")
    ss_api_key = os.getenv("SMARTSUITE_API_KEY")
    ss_workspace_id = os.getenv("SMARTSUITE_WORKSPACE_ID")

    if not all([apollo_key, ss_api_key, ss_workspace_id]):
        print("ERROR: Missing required credentials in .env")
        return

    # Initialize Clients
    apollo = ApolloClient(apollo_key)
    smartsuite = SmartSuiteClient(ss_api_key, ss_workspace_id)

    # CRM Table Constants
    SOLUTION_ID = "69575be937f6f09c44f19154"
    LEADS_TABLE_ID = "6818e4145aa2a5a36b354d60"

    print(f"--- STARTING LEAD GENERATION ---")
    print(f"Criteria: {target_titles} in {target_locations}")
    
    stats = {"found": 0, "synced": 0, "skipped": 0, "errors": 0}

    try:
        leads = apollo.search_people(target_titles, target_locations, limit=limit)
        stats["found"] = len(leads)

        for lead in leads:
            email = lead.get("email")
            name = lead.get("name") or f"{lead.get('first_name')} {lead.get('last_name')}"
            
            if not email:
                print(f"Skipping {name}: No email found.")
                stats["skipped"] += 1
                continue

            # Layer 3 Deduplication logic
            try:
                # Use list_records with a filter for the specific email field (sb8f7c7254)
                # This is more reliable than the global search endpoint
                filter_data = {
                    "filter": {
                        "operator": "and",
                        "rules": [
                            {
                                "field": "sb8f7c7254", # Email field slug
                                "operator": "equal",
                                "value": email
                            }
                        ]
                    },
                    "limit": 1
                }
                existing = smartsuite.list_records(SOLUTION_ID, LEADS_TABLE_ID, filter_data)
                
                if existing.get("total", 0) > 0:
                    print(f"Skipping {email}: Already exists in CRM.")
                    stats["skipped"] += 1
                    continue
            except Exception as e:
                print(f"Deduplication check failed for {email}, proceeding with caution: {e}")

            # Mapping (Apollo -> SmartSuite)
            record_data = {
                "s3e2e7e115": { # Full Name field
                    "first_name": lead.get("first_name", name.split()[0] if name else ""),
                    "last_name": lead.get("last_name", name.split()[-1] if name and " " in name else "")
                },
                "sb8f7c7254": email, # Email (Single field)
                "sec468eef2": lead.get("organization", {}).get("name", "Unknown"), # New Account field
                "description": {
                    "html": f"<p>Imported via Apollo Lead Gen Workflow</p><p><b>Apollo ID:</b> {lead.get('id')}</p><p><b>LinkedIn:</b> <a href='{lead.get('linkedin_url', '#')}'>{lead.get('linkedin_url', 'N/A')}</a></p>"
                },
                "status": {"value": "backlog"} # Default to 'Leads' status
            }

            try:
                smartsuite.create_record(SOLUTION_ID, LEADS_TABLE_ID, record_data)
                print(f"SUCCESS: Synced {name} ({email})")
                stats["synced"] += 1
            except Exception as e:
                print(f"FAILED: Could not create record for {email}: {e}")
                stats["errors"] += 1

    except ApolloExecutionError as e:
        print(f"CRITICAL ERROR: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

    print(f"--- WORKFLOW COMPLETE ---")
    print(f"Summary: Found {stats['found']}, Synced {stats['synced']}, Skipped {stats['skipped']}, Errors {stats['errors']}")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments or use defaults
    titles = ["Owner", "Founder", "President", "Manager"]
    locations = ["Southern California", "Los Angeles", "San Diego", "Orange County"]
    limit = 10

    if len(sys.argv) > 1:
        # Simple parser for orchestration
        try:
            import ast
            # If orchestrator passes a json string or list
            titles = ast.literal_eval(sys.argv[1]) if sys.argv[1].startswith('[') else [sys.argv[1]]
            if len(sys.argv) > 2:
                locations = ast.literal_eval(sys.argv[2]) if sys.argv[2].startswith('[') else [sys.argv[2]]
            if len(sys.argv) > 3:
                limit = int(sys.argv[3])
        except:
            pass

    run_workflow(
        target_titles=titles, 
        target_locations=locations, 
        limit=limit
    )
