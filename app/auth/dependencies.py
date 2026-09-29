from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_token_from_request(request: Request, bearer_token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """
    Extract JWT token either from HTTP Authorization Bearer header
    or from the 'access_token' cookie for browser sessions.
    """
    if bearer_token:
        return bearer_token
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token[7:]
        return cookie_token
    return None

def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> Optional[User]:
    """Returns the current User if authenticated, else None (non-blocking for public pages)."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    email: Optional[str] = payload.get("sub")
    if not email:
        return None
    user = db.query(User).filter(User.email == email).first()
    return user

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
) -> User:
    """Requires authentication. Raises 401 Unauthorized if not authenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or have expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Requires ADMIN role. Raises 403 Forbidden if user is not an administrator."""
    if current_user.role != UserRole.ADMIN.value and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource."
        )
    return current_user
