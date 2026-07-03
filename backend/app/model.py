from app.models.articles import Article
from app.models.users import User
from app.models.keywords import Keyword
from app.models.query import Query
from app.database import SessionLocal
import json


def insert_article(id, title, abstract, id_user, source):
    db = SessionLocal()
    try:
        existing_article = db.query(Article).filter(Article.id == id).first()
        if not existing_article:
            db.add(Article(
                id=id,
                title=title,
                abstract=abstract,
                id_user=id_user,
                source=source
            ))
            db.commit()
        else:
            print("existing article\n")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def insert_keywords_PubMed(keywords, article_id):
    db = SessionLocal()
    try:
        for k in keywords:
            keyword_text = k.get_text(strip=True)
            if not keyword_text:
                continue
            existing_kw = db.query(Keyword).filter(
                Keyword.keyword == keyword_text,
                Keyword.id_article == article_id
            ).first()
            if not existing_kw:
                db.add(Keyword(keyword=keyword_text, id_article=article_id))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def insert_keywords(keywords, article_id):
    db = SessionLocal()
    try:
        for k in keywords:
            existing_kw = db.query(Keyword).filter(
                Keyword.keyword == k,
                Keyword.id_article == article_id
            ).first()
            if not existing_kw:
                db.add(Keyword(keyword=k, id_article=article_id))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def insert_user(email, hashed_password, profil, weekly_monthly, last_updated_date, next_updated_date):
    db = SessionLocal()
    try:
        db.add(User(
            email=email,
            hashed_password=hashed_password,
            profil=profil,
            last_updated_date=last_updated_date,
            next_updated_date=next_updated_date,
            weekly_monthly=weekly_monthly
        ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def insert_query(description, source, id_user):
    db = SessionLocal()
    try:
        db.add(Query(description=description, source=source, id_user=id_user))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_query(id_user):
    db = SessionLocal()
    try:
        return db.query(Query).filter(Query.id_user == id_user).all()
    finally:
        db.close()


def update_user_date(user_id, new_update_date, last_update_date):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_updated_date = last_update_date
            user.next_updated_date = new_update_date
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_articles(id_lists, user_id):
    db = SessionLocal()
    try:
        result = []
        for id_list in id_lists:
            articles = db.query(Article).filter(
                Article.id == id_list,
                Article.id_user == user_id
            ).first()
            if articles:
                result.append({"title": articles.title, "abstract": articles.abstract})
        return json.dumps(result)
    finally:
        db.close()


def get_user(email):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()