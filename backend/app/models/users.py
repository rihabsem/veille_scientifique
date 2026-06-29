from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.articles import Article
from app.models.user_keywords import User_Keywords

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profil = Column(String)
    last_updated_date = Column(String)  #format should be YYYY-MM-DD
    next_updated_date = Column(String)  #format should be YYYY-MM-DD
    weekly_monthly = Column(String)
    articles = relationship("Article", back_populates="user_a")
    user_k = relationship("User_Keywords", back_populates="keyword_u")
    queries_user = relationship("Query", back_populates="users_query")