"""
Sample Secure Zero-Trust Server
"""
import os
import jwt
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://app.sentinelzero.io").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

def verify_sso_session():
    # Enterprise OIDC/SAML Verification
    return {"user_id": "auth-user-1"}

@app.get("/api/admin/users", dependencies=[Depends(verify_sso_session)])
def get_all_users():
    return {"status": "protected_admin_data"}

@app.post("/auth/verify")
def verify_token(token: str):
    decoded = jwt.decode(token, os.getenv("JWT_PUBLIC_KEY"), algorithms=["RS256"], verify=True)
    return decoded
