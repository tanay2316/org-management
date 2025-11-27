from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI=os.getenv("MONGO_URI")
MASTER_DB_NAME=os.getenv("MASTER_DB")
_client=MongoClient(MONGO_URI)
master_db=_client[MASTER_DB_NAME]

def get_master_db(): return master_db

def create_org_collection(name):
    db=_client[MASTER_DB_NAME]
    cname=f"org_{name}"
    if cname not in db.list_collection_names():
        db.create_collection(cname)
    return db[cname]

def drop_org_collection(name):
    db=_client[MASTER_DB_NAME]
    cname=f"org_{name}"
    if cname in db.list_collection_names():
        db.drop_collection(cname)
        return True
    return False

def copy_collection(src,dst):
    db=_client[MASTER_DB_NAME]
    s=f"org_{src}"
    d=f"org_{dst}"
    if s not in db.list_collection_names(): return False
    if d not in db.list_collection_names():
        db.create_collection(d)
    S=db[s]; D=db[d]
    docs=list(S.find({}))
    for x in docs: x.pop("_id",None)
    if docs: D.insert_many(docs)
    return True
