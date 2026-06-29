from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    id_article = Column(String, ForeignKey("articles.id"))

    article = relationship("Article", back_populates="id_keyword")