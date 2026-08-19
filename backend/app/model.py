from app.models.articles import Article
from app.models.users import User
from app.models.keywords import Keyword
from app.models.query import Query
from app.models.passwordReset import PasswordResetToken
from app.database import SessionLocal
from datetime import datetime, timedelta
from sqlalchemy import func
import re
import secrets


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
        db.refresh(new_user)
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
        print(user_id)
        print(update_rate)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        days = 7 if update_rate == "weekly" else 31

        date_obj = datetime.strptime(user.last_updated_date, "%Y-%m-%d").date()
        date_next = date_obj + timedelta(days=days)

        user.weekly_monthly = update_rate
        user.next_updated_date = date_next.isoformat()
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def delete_queries_by_source(user_id):
    db = SessionLocal()
    try:
        db.query(Query).filter(
            Query.id_user == user_id).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def count_queries(user_id):
    db = SessionLocal()
    try:
        count = (
            db.query(func.count(Query.id))
            .filter(Query.id_user == user_id)
            .scalar()
        )
        return count
    finally:
        db.close()

def mark_email_sent(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.email_sent = True
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def reset_email_sent(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.email_sent = False
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def update_search_status(user_id: int, status: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.search_status = status
            db.commit()
    finally:
        db.close()


def get_search_status(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user.search_status
        return None
    finally:
        db.close()

def create_reset_token(user_id):
    db = SessionLocal()
    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        reset_entry = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(reset_entry)
        db.commit()
        return token
    finally:
        db.close()

def verify_reset_token(token):
    db = SessionLocal()
    try:
        entry = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == 0
        ).first()
        if entry is None:
            return None
        if entry.expires_at < datetime.now():
            return None
        return entry.user_id
    finally:
        db.close()

def mark_token_used(token):
    db = SessionLocal()
    try:
        entry = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        if entry:
            entry.used = 1
            db.commit()
    finally:
        db.close()

def update_user_password(user_id, new_hashed_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.hashed_password = new_hashed_password
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()