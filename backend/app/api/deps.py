from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token

bearer = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    try:
        payload = decode_token(credentials.credentials)
        return {
            "user_id": payload["sub"],
            "org_id": payload["org_id"]
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")