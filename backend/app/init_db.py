from app.database import Base, engine
from app.models.users import User
from app.models.articles import Article
from app.models.keywords import Keyword

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

if __name__ == "__main__":
    init_db()
