from pydantic import BaseModel,EmailStr,Field

class OrgCreateRequest(BaseModel):
    organization_name:str
    email:EmailStr
    password:str

class OrgUpdateRequest(BaseModel):
    organization_name:str
    new_organization_name:str
    email:EmailStr|None=None
    password:str|None=None

class AdminLoginRequest(BaseModel):
    email:EmailStr
    password:str
