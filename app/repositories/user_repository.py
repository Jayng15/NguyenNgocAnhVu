from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserPublic

class UserRepository:
    """
    Repository class for user-related database operations.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreate) -> UserPublic:
        """
        Create a new user and return as UserPublic schema.

        Args:
            user_data (UserCreate): The user data to create.

        Returns:
            UserPublic: The created user data.
        """
        if self.get_user_by_email(user_data.email):
            raise ValueError("User with this email already exists.")
        
        new_user = User(**user_data.model_dump())
        self.db_session.add(new_user)
        self.db_session.commit()
        self.db_session.refresh(new_user)
        
        return UserPublic(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at
        )
    
    async def get_users(self) -> list[UserPublic]:
        """
        Retrieve all users and return as a list of UserPublic schemas.
        """
        users = self.db_session.query(User).all()
        return [
            UserPublic(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at
            ) for user in users
        ]

    async def get_user_by_email(self, email: str) -> UserPublic | None:
        """
        Retrieve a user by email and return as UserPublic schema.
        """
        user = self.db_session.query(User).filter(User.email == email).first()
        return UserPublic(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        ) if user else None