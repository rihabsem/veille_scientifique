from app.models.articles import Article
from app.models.users import User
from app.models.keywords import Keyword
from app.models.query import Query
from app.database import SessionLocal
import json
from datetime import datetime, timedelta
import re


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


def insert_user(name, email, hashed_password, profil, last_updated_date, next_updated_date, weekly_monthly):
    db = SessionLocal()
    try:
        new_user = User(
            nom=name,
            email=email,
            hashed_password=hashed_password,
            profil=profil,
            last_updated_date=last_updated_date,
            next_updated_date=next_updated_date,
            weekly_monthly=weekly_monthly
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # recharge l'objet depuis la DB pour récupérer l'id auto-généré
        return new_user.id
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
                result.append({"id": articles.id, "title": articles.title, "abstract": articles.abstract, "source": articles.source})
        return result
    finally:
        db.close()


def get_user(email):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def get_user_by_id(user_id):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

def get_user_profile(user_id):
    db = SessionLocal()
    try:
        return db.query(User.profil).filter(User.id == user_id).first()
    finally:
        db.close()

def get_user_by_date(next_update_date):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.next_updated_date == next_update_date).all()
    finally:
        db.close()

def get_articles_by_date(user_id, last_updated_date, next_updated_date):
    db = SessionLocal()
    try:
        return db.query(Article).join(
            User, Article.id_user == User.id
        ).filter(
            User.id == user_id,
            User.last_updated_date == last_updated_date,
            User.next_updated_date == next_updated_date
        ).all()
    finally:
        db.close()

def update_user_profile(user_id, profile):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.profil = profile
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def update_user_update_rate(user_id, update_rate):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if update_rate == "weekly":
                days = 7
            else :
                days = 31
            date = user.last_updated_date
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            date_next = date+timedelta(days=days)
            date_next_string = re.sub(r"\d{2}:\d{2}:\d{2}\.\d+", "", str(date_next)).strip()
            user.next_updated_date = date_next_string
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

