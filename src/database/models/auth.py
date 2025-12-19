import bcrypt
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.database.models.base import Base

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    role_name = Column(String, unique=True, nullable=False)
    role_description = Column(String)

class AppUser(Base):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

    roles = relationship("Role", secondary="user_role")

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class UserRole(Base):
    __tablename__ = "user_role"

    app_user_id = Column(Integer, ForeignKey("app_user.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)