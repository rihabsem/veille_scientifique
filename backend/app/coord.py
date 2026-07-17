from app.database import SessionLocal
from app.models.query import Query
from app.api_logic import pubmed_search, pubmed_fetch, semantic_scholar_search, clinical_trials_search, handle_response_clinical_trials, handle_result_pubmed, handle_result_semantic_scholar
from app.vector_db_creation import delete_old_articles, search_articles_for_user
from app.model import update_user_date, get_user_by_date
import time
from datetime import datetime, timedelta
import re
from app.email_service import send_email

def process_user(db, user):
    delete_old_articles(user.id)
    queries = db.query(Query).filter(Query.id_user == user.id).all()

    if user.weekly_monthly == "weekly":
        days_to_add = 7
    elif user.weekly_monthly == "monthly":
        days_to_add = 31
    else:
        print(f"Utilisateur {user.id} : weekly_monthly invalide ({user.weekly_monthly})")
        return None

    for query in queries:
        if query.source == "PubMed":
            last_updated_date = re.sub("-", "/", user.last_updated_date)
            next_updated_date = re.sub("-", "/", user.next_updated_date)
            pmids = pubmed_search(query.description, last_updated_date, next_updated_date)
            time.sleep(3)
            res_pubmed = pubmed_fetch(pmids)
            if res_pubmed is not None:
                handle_result_pubmed(res_pubmed.text, user.id)
            time.sleep(1)

        elif query.source == "Semantic Scholar":
            res_semantic = semantic_scholar_search(query.description, user.last_updated_date, user.next_updated_date)
            handle_result_semantic_scholar(res_semantic.json(), user.id)
            time.sleep(1)

        elif query.source == "Clinical Trials":
            res_clinical_trials = clinical_trials_search(query.description, user.last_updated_date, user.next_updated_date)
            handle_response_clinical_trials(res_clinical_trials, user.id)
            time.sleep(1)

        time.sleep(5)
    print("1")
    resultats = search_articles_for_user(user.id)
    print("2")
    print(f"the search results for user {user.id} are {resultats}")
    date = datetime.now()
    date_next = date + timedelta(days=days_to_add)
    user_last_updated_date = str(date.strftime("%Y-%m-%d"))
    user_next_updated_date = str(date_next.strftime("%Y-%m-%d"))
    update_user_date(user.id, user_next_updated_date, user_last_updated_date)
    return resultats


def run_batch():
    """Appelée par le scheduler, une fois par jour. Traite tous les utilisateurs dus aujourd'hui."""
    print("coordinateur on")
    db = SessionLocal()
    try:
        date = datetime.now()
        date_string = re.sub("[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9]+", "", str(date)).strip()
        users = get_user_by_date(date_string)
        print(f"number of users to process = {len(users)}")

        for user in users:
            try:
                process_user(db, user)
                
            except Exception as e:
                print(f"Erreur pour l'utilisateur {user.id}: {e}")
    finally:
        db.close()


