#!/usr/bin/env python3
"""
Check which organization is associated with tanayj16@gmail.com
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MASTER_DB_NAME = os.getenv("MASTER_DB")

if not MONGO_URI:
    print("ERROR: MONGO_URI not set in .env")
    exit(1)

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client[MASTER_DB_NAME]

print(f"Database: {MASTER_DB_NAME}")
print(f"Collections: {db.list_collection_names()}\n")

# Find admin by email
email = "tanayj16@gmail.com"
print(f"Looking up admin with email: {email}")
admin = db["admins"].find_one({"email": email.lower()})

if admin:
    print(f"✓ Admin found!")
    print(f"  Admin ID: {admin.get('_id')}")
    print(f"  Email: {admin.get('email')}")
    print(f"  Organization: {admin.get('organization_name')}")
    print(f"  Password hash: {admin.get('password')[:20]}...")
else:
    print(f"✗ Admin with email '{email}' not found")
    print("\nAll admins in database:")
    for admin in db["admins"].find({}):
        print(f"  - Email: {admin.get('email')}, Org: {admin.get('organization_name')}")

# Check if testorg exists
print(f"\nLooking up organization: testorg")
testorg = db["organizations"].find_one({"organization_name": "testorg"})
if testorg:
    print(f"✓ Organization 'testorg' found!")
    print(f"  Admin User ID: {testorg.get('admin_user_id')}")
    print(f"  Collection Name: {testorg.get('collection_name')}")
else:
    print(f"✗ Organization 'testorg' not found")
    print("\nAll organizations in database:")
    for org in db["organizations"].find({}):
        print(f"  - Name: {org.get('organization_name')}, Admin: {org.get('admin_user_id')}")

print("\n" + "="*70)
print("CONCLUSION:")
admin = db["admins"].find_one({"email": email.lower()})
if admin:
    org_name = admin.get("organization_name")
    print(f"Admin '{email}' belongs to organization: '{org_name}'")
    print(f"To delete this organization, use: /org/delete?name={org_name}")
else:
    print("Admin not found. Need to create org first with /org/create")
