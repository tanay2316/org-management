#!/usr/bin/env python3
"""
Diagnostic script to identify the 403 Forbidden issue with DELETE /org/delete
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("DIAGNOSTIC: DELETE /org/delete 403 Forbidden")
print("=" * 70)

# Check what orgs exist
print("\n[1] Checking existing organizations...")
try:
    resp = requests.get(f"{BASE_URL}/org/get?name=testorg")
    if resp.status_code == 200:
        org = resp.json()
        print(f"✓ Organization found: {json.dumps(org, indent=2)}")
    else:
        print(f"✗ Organization not found (status {resp.status_code})")
except Exception as e:
    print(f"✗ Error: {e}")

# Try to delete WITHOUT token (this should fail with 403)
print("\n[2] Attempting DELETE without Bearer token...")
try:
    resp = requests.delete(f"{BASE_URL}/org/delete?name=testorg")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")

# Check if we have any admin accounts
print("\n[3] Checking available admin accounts...")
print("(Note: This requires direct DB access, skipping for now)")

# Now try the complete flow: create -> login -> delete
print("\n[4] FULL WORKFLOW: Create org -> Login -> Delete with token")
print("-" * 70)

# Create org with unique name
org_name = "deletetest"
email = f"admin@{org_name}.com"
password = "TestPass123!"

print(f"\n  Creating org: {org_name}")
resp = requests.post(f"{BASE_URL}/org/create", json={
    "organization_name": org_name,
    "email": email,
    "password": password
})
print(f"  Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"  Error: {resp.json()}")
else:
    print(f"  ✓ Created successfully")

print(f"\n  Logging in as {email}")
resp = requests.post(f"{BASE_URL}/admin/login", json={
    "email": email,
    "password": password
})
print(f"  Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"  Error: {resp.json()}")
else:
    data = resp.json()
    token = data.get("access_token")
    print(f"  ✓ Login successful")
    print(f"  Token (first 50 chars): {token[:50]}...")
    
    # Decode token to see what's in it
    import base64
    parts = token.split('.')
    if len(parts) >= 2:
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        try:
            decoded = base64.urlsafe_b64decode(payload)
            print(f"  Token payload: {decoded.decode()}")
        except:
            pass
    
    print(f"\n  Deleting org with token...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(f"{BASE_URL}/org/delete?name={org_name}", headers=headers)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")
    
    if resp.status_code == 200:
        print(f"  ✓ Delete successful!")
    else:
        print(f"  ✗ Delete failed")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
