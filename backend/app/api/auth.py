from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача"""
    user = AuthService.register_user(db, user_data)
    
    # Автоматичний вхід після реєстрації
    login_data = UserLogin(username=user.username, password=user_data.password)
    user, access_token = AuthService.authenticate_user(db, login_data)
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вхід користувача"""
    user, access_token = AuthService.authenticate_user(db, login_data)
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Отримання інформації про поточного користувача"""
    return UserResponse.model_validate(current_user)
