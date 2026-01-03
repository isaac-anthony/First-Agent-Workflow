#!/usr/bin/env python3
"""
Test script for SmartSuite API Client
Use this to verify your API credentials and test basic operations
"""

import os
import sys
from dotenv import load_dotenv
from smartsuite_client import SmartSuiteClient

load_dotenv()

def main():
    """Test SmartSuite client connection."""
    api_key = os.getenv('SMARTSUITE_API_KEY')
    workspace_id = os.getenv('SMARTSUITE_WORKSPACE_ID')
    
    if not api_key:
        print("Error: SMARTSUITE_API_KEY not found in .env", file=sys.stderr)
        sys.exit(1)
    
    if not workspace_id:
        print("Error: SMARTSUITE_WORKSPACE_ID not found in .env", file=sys.stderr)
        sys.exit(1)
    
    print("Initializing SmartSuite client...")
    client = SmartSuiteClient(api_key, workspace_id)
    
    print("\nTesting connection by listing solutions...")
    try:
        solutions = client.list_solutions()
        print(f"✓ Successfully connected! Found {len(solutions)} solution(s)")
        
        if solutions:
            print("\nAvailable solutions:")
            for solution in solutions[:5]:  # Show first 5
                solution_id = solution.get('id', 'N/A')
                solution_name = solution.get('name', 'N/A')
                print(f"  - {solution_name} (ID: {solution_id})")
        
        print("\n✓ SmartSuite client is working correctly!")
        return 0
    
    except Exception as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Verify your Workspace ID is correct (8 characters)")
        print("3. Check your internet connection")
        print("4. Verify API key has proper permissions")
        return 1

if __name__ == '__main__':
    sys.exit(main())



