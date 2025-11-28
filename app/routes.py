from fastapi import APIRouter,HTTPException,Depends
from app.models import OrgCreateRequest,OrgUpdateRequest,AdminLoginRequest
from app.db import get_master_db,create_org_collection,drop_org_collection,copy_collection
from app.auth import hash_password,verify_password,create_access_token,get_current_admin

router=APIRouter()
ORG="organizations"; ADM="admins"

@router.post("/org/create")
def create_org(r:OrgCreateRequest):
    db=get_master_db()
    orgs=db[ORG]; admins=db[ADM]
    name=r.organization_name.lower()
    if orgs.find_one({"organization_name":name}):
        raise HTTPException(400,"Exists")
    create_org_collection(name)
    aid=admins.insert_one({"email":r.email,"password":hash_password(r.password),"organization_name":name}).inserted_id
    orgs.insert_one({"organization_name":name,"collection_name":f"org_{name}","admin_user_id":aid})
    return {"status":"success"}

@router.get("/org/get")
def get_org(name:str):
    db=get_master_db()
    org=db[ORG].find_one({"organization_name":name.lower()})
    if not org: raise HTTPException(404,"Not found")
    org["admin_user_id"]=str(org["admin_user_id"]); org["_id"]=str(org["_id"])
    return org

@router.put("/org/update")
def update_org(r:OrgUpdateRequest,cur=Depends(get_current_admin)):
    db=get_master_db()
    orgs=db[ORG]; admins=db[ADM]
    old=r.organization_name.lower(); new=r.new_organization_name.lower()
    if cur["org_name"]!=old: raise HTTPException(403,f"No access. Token org: '{cur['org_name']}', requested org: '{old}'")
    if orgs.find_one({"organization_name":new}): raise HTTPException(400,"New exists")
    copy_collection(old,new)
    orgs.update_one({"organization_name":old},{"$set":{"organization_name":new,"collection_name":f"org_{new}"}})
    return {"status":"updated"}

@router.delete("/org/delete")
def delete_org(name:str,cur=Depends(get_current_admin)):
    if cur["org_name"]!=name.lower(): raise HTTPException(403,f"No access. Token org: '{cur['org_name']}', requested org: '{name.lower()}'")
    drop_org_collection(name.lower())
    db=get_master_db(); db[ORG].delete_one({"organization_name":name.lower()})
    db[ADM].delete_many({"organization_name":name.lower()})
    return {"status":"deleted"}

@router.post("/admin/login")
def login(r:AdminLoginRequest):
    db=get_master_db(); adm=db[ADM].find_one({"email":r.email.lower()})
    if not adm or not verify_password(r.password,adm["password"]): raise HTTPException(401,"Bad creds")
    t=create_access_token({"admin_id":str(adm["_id"]),"org_name":adm["organization_name"]})
    return {"access_token":t}
