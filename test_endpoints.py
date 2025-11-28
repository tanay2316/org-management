#!/usr/bin/env python3
"""
Test script for org-management API endpoints
Demonstrates the proper workflow to update an organization
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_org_workflow():
    print("=" * 60)
    print("Testing Org Management API")
    print("=" * 60)
    
    # Step 1: Create organization
    print("\n[1] Creating organization 'myorg'...")
    create_payload = {
        "organization_name": "myorg",
        "email": "admin@myorg.com",
        "password": "SecurePassword123!"
    }
    resp = requests.post(f"{BASE_URL}/org/create", json=create_payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    if resp.status_code != 200:
        print("Failed to create org. Exiting.")
        return
    
    # Step 2: Login to get token
    print("\n[2] Logging in with admin credentials...")
    login_payload = {
        "email": "admin@myorg.com",
        "password": "SecurePassword123!"
    }
    resp = requests.post(f"{BASE_URL}/admin/login", json=login_payload)
    print(f"Status: {resp.status_code}")
    resp_data = resp.json()
    print(f"Response: {resp_data}")
    
    if resp.status_code != 200:
        print("Failed to login. Exiting.")
        return
    
    token = resp_data.get("access_token")
    print(f"Token obtained: {token[:20]}...")
    
    # Step 3: Get organization details
    print("\n[3] Fetching organization details...")
    resp = requests.get(f"{BASE_URL}/org/get?name=myorg")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    
    # Step 4: Update organization (WITH TOKEN)
    print("\n[4] Updating organization name to 'myorg_updated'...")
    update_payload = {
        "organization_name": "myorg",
        "new_organization_name": "myorg_updated"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    resp = requests.put(f"{BASE_URL}/org/update", json=update_payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    if resp.status_code == 200:
        print("\n✓ Update successful!")
    else:
        print("\n✗ Update failed. Ensure token is valid and org name matches.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        test_org_workflow()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to http://localhost:8000")
        print("Ensure the uvicorn server is running:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
