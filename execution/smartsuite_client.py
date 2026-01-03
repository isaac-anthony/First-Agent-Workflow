#!/usr/bin/env python3
"""
SmartSuite API Client
Deterministic wrapper for SmartSuite REST API operations
"""

import requests
from typing import Optional, Dict, Any, List
import json


class SmartSuiteClient:
    """Client for interacting with SmartSuite API."""
    
    BASE_URL = "https://app.smartsuite.com/api/v1"
    
    def __init__(self, api_key: str, workspace_id: str):
        """
        Initialize SmartSuite client.
        
        Args:
            api_key: SmartSuite API key
            workspace_id: SmartSuite workspace ID (8 characters)
        """
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Account-Id": workspace_id,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to SmartSuite API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Optional request body
        
        Returns:
            Response JSON as dict
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def list_solutions(self) -> List[Dict[str, Any]]:
        """List all solutions in the workspace."""
        return self._make_request("GET", "/solutions/")
    
    def get_solution(self, solution_id: str) -> Dict[str, Any]:
        """Get solution details including tables."""
        return self._make_request("GET", f"/solutions/{solution_id}/")
    
    def list_records(
        self, 
        solution_id: str, 
        table_id: str, 
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        List records from a table.
        
        Args:
            solution_id: Solution ID (not used in newer endpoint style but kept for compatibility)
            table_id: Table ID (Application ID)
            filters: Optional filters dict
        """
        # Always use the POST list endpoint
        endpoint = f"/applications/{table_id}/records/list/"
        return self._make_request("POST", endpoint, filters or {})
    
    def get_record(
        self, 
        solution_id: str, 
        table_id: str, 
        record_id: str
    ) -> Dict[str, Any]:
        """Get a specific record."""
        endpoint = f"/applications/{table_id}/records/{record_id}/"
        return self._make_request("GET", endpoint)
    
    def create_record(
        self, 
        solution_id: str, 
        table_id: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record."""
        endpoint = f"/applications/{table_id}/records/"
        return self._make_request("POST", endpoint, data)
    
    def update_record(
        self, 
        solution_id: str, 
        table_id: str, 
        record_id: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record."""
        endpoint = f"/applications/{table_id}/records/{record_id}/"
        return self._make_request("PUT", endpoint, data)
    
    def delete_record(
        self, 
        solution_id: str, 
        table_id: str, 
        record_id: str
    ) -> Dict[str, Any]:
        """Delete a record."""
        endpoint = f"/applications/{table_id}/records/{record_id}/"
        return self._make_request("DELETE", endpoint)
    
    def search_records(
        self, 
        solution_id: str, 
        table_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """Search records with a query."""
        endpoint = f"/applications/{table_id}/records/search/"
        return self._make_request("POST", endpoint, {"query": query})
    
    def get_table_metadata(self, table_id: str) -> Dict[str, Any]:
        """
        Get table metadata including field definitions.
        
        Args:
            table_id: Table/Application ID
        
        Returns:
            Dictionary containing table metadata with 'structure' field containing all field definitions
        """
        return self._make_request("GET", f"/applications/{table_id}/")
    
    def get_field_mappings(self, table_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get field mappings (slug -> label, type, options) for a table.
        
        Args:
            table_id: Table/Application ID
        
        Returns:
            Dictionary mapping field slugs to field metadata:
            {
                "field_slug": {
                    "slug": "field_slug",
                    "label": "Field Label",
                    "type": "field_type",
                    "options": ["option1", "option2"],  # if applicable
                    "option_labels": {"option1": "Option 1", ...}  # if applicable
                }
            }
        """
        metadata = self.get_table_metadata(table_id)
        structure = metadata.get('structure', [])
        
        field_mappings = {}
        for field in structure:
            if isinstance(field, dict):
                slug = field.get('slug', '')
                label = field.get('label', 'N/A')
                field_type = field.get('field_type', 'N/A')
                params = field.get('params', {})
                
                field_info = {
                    'slug': slug,
                    'label': label,
                    'type': field_type,
                    'params': params
                }
                
                # Extract options if available
                if 'choices' in params:
                    choices = params['choices']
                    field_info['options'] = [
                        choice.get('value') 
                        for choice in choices 
                        if isinstance(choice, dict)
                    ]
                    field_info['option_labels'] = {
                        choice.get('value'): choice.get('label') 
                        for choice in choices 
                        if isinstance(choice, dict)
                    }
                
                field_mappings[slug] = field_info
        
        return field_mappings

