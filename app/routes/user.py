from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import app
from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserPublic


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    operation_id="create_user",
    response_model=UserPublic,
)
def create_user(
    user: UserCreate, repo: UserRepository = Depends(get_user_repository)
) -> UserPublic:
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
        user_public = repo.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return user_public


@router.get(
    "/",
    summary="Get users with id filter",
    status_code=status.HTTP_200_OK,
    operation_id="get_users",
    response_model=list[UserPublic] | UserPublic,
)
def get_users(
    id: UUID | None = Query(None, description="Filter users by ID"),
    repo: UserRepository = Depends(get_user_repository),
) -> list[UserPublic] | UserPublic:
    """
    Retrieve all users or filter by ID.

    Args:
        id (int | None): Optional user ID to filter by.
        repo (UserRepository): The user repository dependency.

    Returns:
        list[UserPublic]: A list of user data.
    """
    if id is not None:
        user = repo.get_user_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    return repo.get_users()
