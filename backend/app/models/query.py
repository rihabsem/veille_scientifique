from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    source = Column(String, index=True)
    id_user = Column(Integer, ForeignKey("users.id"))
    users_query = relationship("User", back_populates="queries_user")