from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User_Keywords(Base):
    __tablename__ = "user_keywords"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    id_user = Column(Integer, ForeignKey("users.id"))

    keyword_u = relationship("User", back_populates="user_k")