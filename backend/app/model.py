from app.models.articles import Article
from app.models.users import User
from app.models.keywords import Keyword
from app.models.query import Query
from app.database import SessionLocal
import json

db=SessionLocal()
def insert_article(id, title, abstract, id_user, source):
    existing_article = db.query(Article).filter(Article.id == id).first()

    if not existing_article:
        new_article = Article(
            id=id,
            title=title,
            abstract=abstract,
            id_user=id_user,
            source = source
            )
        db.add(new_article)

    else:
        print("existing article\n")

    db.commit()
    db.close()

def insert_keywords_PubMed(keywords, article_id):
    for k in keywords:
        keyword_text = k.get_text(strip=True)
        if not keyword_text :
            continue
        existing_kw = db.query(Keyword).filter(
            Keyword.keyword == keyword_text,
            Keyword.id_article == article_id
        ).first()
        if not existing_kw:
            db.add(Keyword(
                keyword = keyword_text,
                id_article = article_id
            ))
    db.commit()
    db.close()

def insert_keywords_PubMed(keywords, article_id):
    for k in keywords:
        keyword_text = k.get_text(strip=True)
        if not keyword_text :
            continue
        existing_kw = db.query(Keyword).filter(
            Keyword.keyword == keyword_text,
            Keyword.id_article == article_id
        ).first()
        if not existing_kw:
            db.add(Keyword(
                keyword = keyword_text,
                id_article = article_id
            ))
    db.commit()
    db.close()

def insert_keywords(keywords, article_id):
    for k in keywords:
        existing_kw = db.query(Keyword).filter(
            Keyword.keyword == k,
            Keyword.id_article == article_id
        ).first()
        if not existing_kw:
            db.add(Keyword(
                keyword = k,
                id_article = article_id
            ))
    db.commit()
    db.close()

def insert_user(email,hashed_password, profil, weekly_monthly,last_updated_date, next_updated_date):
    db.add(User(
        email = email,
        hashed_password = hashed_password,
        profil = profil,
        last_updated_date = last_updated_date,
        next_updated_date = next_updated_date,
        weekly_monthly = weekly_monthly
    ))
    db.commit()
    db.close()

def insert_query(description, source, id_user):
    db.add(Query(
        description = description,
        source = source,
        id_user = id_user
    ))
    db.commit()
    db.close()

def get_query(id_user):
    queries = db.query(Query).filter(
        id_user == id_user
    ).all()
    return queries 

def update_user_date(user_id, new_update_date, last_update_date):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_updated_date = last_update_date
        user.next_updated_date = new_update_date
        db.commit()
        db.close()

def get_articles(id_lists, user_id):
    dic = {}
    list=[]
    for id_list in id_lists:
        articles = db.query(Article).filter(
            Article.id == id_list,
            Article.id_user == user_id
        ).first()
        dic["title"] = articles.title
        dic["abstract"] = articles.abstract
        list.append(dic)
        dic={}
    json_list = json.dumps(list)
    return json_list

def get_user(email):
    query = db.query(User).filter(
        User.email == email
    ).first()
    if query :
        return query
    else:
        return None


        



