from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.keywords import Keyword

class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    abstract = Column(String)
    source = Column(String)
    id_user = Column(Integer, ForeignKey("users.id"))

    id_keyword = relationship("Keyword", back_populates="article")
    user_a = relationship("User", back_populates="articles")

