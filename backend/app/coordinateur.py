from app.database import SessionLocal
from app.models.users import User
from app.models.articles import Article
from app.models.keywords import Keyword
from app.models.query import Query
from app.api_logic import pubmed_search, pubmed_fetch, semantic_scholar_search, clinical_trials_search, handle_response_clinical_trials, handle_result_pubmed, handle_result_semantic_scholar
from app.vector_db_creation import delete_old_articles, search_articles_for_user
from app.model import update_user_date
import time
from datetime import datetime, timedelta
import re


def run():
    print("coordinateur on")
    queries = []
    db = SessionLocal()
    id = 1
    user = db.query(User).filter(User.id == id).first()
    date = datetime.now()
    date_string = re.sub("[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9]+", "",str(date)).strip()
    if(date_string == user.next_updated_date):
        delete_old_articles(id)
        queries = db.query(Query).filter(Query.id_user == id).all()
        if(user.weekly_monthly == "weekly"):
            for query in queries :
                if(query.source == "PubMed"):
                    last_updated_date = re.sub("-","/",user.last_updated_date)
                    next_updated_date = re.sub("-","/",user.next_updated_date)
                    pmids = pubmed_search(query.description, last_updated_date, next_updated_date)
                    time.sleep(3)
                    res_pubmed = pubmed_fetch(pmids)
                    if res_pubmed is not None:
                        handle_result_pubmed(res_pubmed.text, id)
                elif(query.source == "Semantic Scholar"):
                    res_semantic = semantic_scholar_search(query.description, user.last_updated_date, user.next_updated_date)
                    handle_result_semantic_scholar(res_semantic.json(),id)
                elif(query.source == "Clinical Trials"):
                    res_clinical_trials = clinical_trials_search(query.description, user.last_updated_date, user.next_updated_date)
                    handle_response_clinical_trials(res_clinical_trials,id)
                time.sleep(5)
            resultats = search_articles_for_user(id)
            print(f"the search results are {resultats}")
            
            date_next = date + timedelta(days=7)
            user_last_updated_date = str(date.strftime("%Y-%m-%d"))
            user_next_updated_date = str(date_next.strftime("%Y-%m-%d"))
            update_user_date(id,user_next_updated_date, user_last_updated_date)



        elif(user.weekly_monthly == "monthly"):
            for query in queries :
                if(query.source == "PubMed"):
                    print("PUBMED")
                    print(f"*{query.description}*")
                    last_updated_date = re.sub("-","/",user.last_updated_date)
                    next_updated_date = re.sub("-","/",user.next_updated_date)
                    print(f"{last_updated_date} {next_updated_date}")
                    pmids = pubmed_search(query.description, last_updated_date, next_updated_date)
                    time.sleep(3)
                    res_pubmed = pubmed_fetch(pmids)
                    if res_pubmed is not None:
                        handle_result_pubmed(res_pubmed.text, id)

                    time.sleep(1)
                elif(query.source == "Semantic Scholar"):
                    print(f"*{query.description}*")
                    print("SEMANTIC SCHOLAR")
                    print(f"{user.last_updated_date} {user.next_updated_date}")
                    res_semantic = semantic_scholar_search(query.description, user.last_updated_date, user.next_updated_date)
                    handle_result_semantic_scholar(res_semantic.json(),id)
                    time.sleep(1)
                elif(query.source == "Clinical Trials"):
                    print(f"*{query.description}*")
                    print("CLINICAL TRIALS")
                    print(f"{user.last_updated_date} {user.next_updated_date}")
                    res_clinical_trials = clinical_trials_search(query.description, user.last_updated_date, user.next_updated_date)
                    handle_response_clinical_trials(res_clinical_trials,id)
                    time.sleep(1)
                time.sleep(5)
            resultats = search_articles_for_user(id)
            print(f"the search results are {resultats}")
            date_next = date + timedelta(days=31)
            user_last_updated_date = str(date.strftime("%Y-%m-%d"))
            user_next_updated_date = str(date_next.strftime("%Y-%m-%d"))
            update_user_date(id,user_next_updated_date, user_last_updated_date)


if __name__ == "__main__":
    run()

    



    

    
