"""
Sample Vulnerable Backend Server for Testing SentinelZero
"""
import jwt
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# VULN 1: Hardcoded OpenAI API Key (SZ-001)
OPENAI_API_KEY = "sk-live-99182390812903810293810928301982"

# VULN 2: Hardcoded Database URI with credentials (SZ-009)
DATABASE_URL = "postgres://admin_user:SuperSecretPassword992@db.production.internal:5432/core_db"

# VULN 3: Overly permissive CORS wildcard (SZ-003)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VULN 4: Hardcoded DEBUG flag (SZ-010)
DEBUG = True

# VULN 5: Privileged Admin route missing SSO / Auth Guard (SZ-005)
@app.get("/api/admin/users")
def get_all_users():
    return {"status": "unprotected_admin_data"}

# VULN 6: JWT decode with verify=False (SZ-004)
@app.post("/auth/verify")
def verify_token(token: str):
    decoded = jwt.decode(token, "some_secret", verify=False)
    return decoded

# VULN 7: Insecure Deserialization via pickle (SZ-008)
@app.post("/session/restore")
def restore_session(raw_data: bytes):
    session = pickle.loads(raw_data)
    return session
