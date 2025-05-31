from fastapi import APIRouter, Depends, HTTPException, status, Query 
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserPublic
from app.db import get_db
from app.repositories.user_repository import UserRepository

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    Dependency to get the UserRepository instance.
    
    Args:
        db (Session): The database session dependency.
    
    Returns:
        UserRepository: An instance of UserRepository.
    """
    return UserRepository(db)

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post(
    '/',
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,)
async def create_user(
    user: UserCreate,
    repo: UserRepository = Depends(get_user_repository)) -> UserPublic:
    """
    Create a new user in the system.
    
    Args:
        user (UserCreate): The user data to create.
        repo (UserRepository): The user repository dependency.
    
    Returns:
        UserPublic: The created user data. 

    Raises:
        HTTPException: If the user already exists or if there is a validation error.
    """
    try:
        user_public = await repo.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return user_public

@router.get(
    '/',
    summary="Get users with email filter",
    status_code=status.HTTP_200_OK,
    response_model=list[UserPublic],
)
async def get_users(
    email: str = Query(None, description="Filter users by email"),
    repo: UserRepository = Depends(get_user_repository)) -> list[UserPublic]:
    """
    Retrieve a list of users, optionally filtered by email.
    
    Args:
        email (str): Optional email filter for users.
        repo (UserRepository): The user repository dependency.
    
    Returns:
        list[UserPublic]: A list of user data.
    """
    if email:
        user = await repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return [user]
    users = await repo.get_users()
    return users

