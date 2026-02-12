from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep, get_session
from sqlmodel import Session
from app.models import RegularUser, User
from app.auth import encrypt_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_session)]
):
    user = db.exec(select(RegularUser).where(User.username == form_data.username)).one_or_none()
    if not user or not verify_password(plaintext_password=form_data.password, encrypted_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.id, "role": user.role},)

    return {"access_token":access_token, "token_type": "bearer"}

@auth_router.get("/identify")
def get_user_by_id(db: Annotated[Session, Depends(get_session)], user: User = Depends(get_current_user)):
    return user

