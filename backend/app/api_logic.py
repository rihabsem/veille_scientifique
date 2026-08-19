import requests
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup
import time
from app.data_cleaning import clean_data, get_embedding
from app.vector_db_creation import store_embedding_in_db
from app.database import SessionLocal
from app.model import insert_article, insert_keywords, insert_keywords_PubMed

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
semantic_url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
clinical_trials_url = "https://clinicaltrials.gov/api/v2/studies"

def pubmed_search(query, min_date, max_date):

    params = {
        "db": "pubmed",
        "term": query,
        "datetype": "pdat",
        "mindate": min_date,
        "maxdate": max_date,
        "retmode": "json"
    }

    try:
        response = requests.get(search_url, params=params, timeout=30)
    except requests.RequestException as e:
        print(f"Error fetching PubMed search: {e}")
        return []

    raw = response.text

    print("\n[DEBUG] RAW RESPONSE (first 500 chars):")
    print(raw[:500])

    # 1. try JSON
    try:
        data = response.json()

        idlist = data.get("esearchresult", {}).get("idlist", [])

        return idlist

    except Exception as e:
        print("\n[DEBUG] JSON PARSE FAILED:", str(e))
    try:
        root = ET.fromstring(raw)

        ids = [id_elem.text for id_elem in root.findall(".//Id")]

        return ids

    except Exception as e:
        print("\n[DEBUG] XML PARSE FAILED:", str(e))

    return []

def pubmed_fetch(pmids):
    if not pmids:
        print("PubMed: no PMIDs to fetch")
        return None 
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    try:
        response = requests.get(fetch_url, params=params, timeout=30)
        return response
    except requests.RequestException as e:
        print(f"Error fetching PubMed articles: {e}")
        return None

def handle_result_pubmed(results, user_id):
    if results is None:
        print("PubMed: no articles found")
        return
    response = BeautifulSoup(results, "xml")
    articles = response.find_all('PubmedArticle')
    
    for i, article in enumerate(articles, 1):
        pmid_tag = article.find('PMID')
        pmid_tag = pmid_tag.get_text(strip=True)

        title = article.find("ArticleTitle")
        title = title.get_text(strip=True) if title else ""

        abstract = article.find('Abstract')
        abstract = abstract.get_text(strip=True) if abstract else ""

        publisher_name = article.find('CopyrightInformation')
        publisher_name = publisher_name.get_text(strip=True) if publisher_name else "None"

        keywords = article.find_all("Keyword")
        
        keywords_full = " ".join(k.get_text(strip=True) for k in keywords)

        data = f"{title} {keywords_full} {abstract}"
        cleaned_data = clean_data(data)
        embedding = get_embedding(cleaned_data)
        store_embedding_in_db(pmid_tag, embedding, user_id)
        insert_article(pmid_tag, title, abstract, user_id, "PubMed")
        insert_keywords_PubMed(keywords, pmid_tag)


#----------------- Semantic scholar Logic ------------------
def semantic_scholar_search(query, min_date, max_date):
    params = {
    "query": query,
    "fields": "paperId,title,abstract,year,publicationDate",
    "limit": 100,
    "publicationDateOrYear" : f"{min_date}:{max_date}"
    }
    headers = {
    "x-api-key": os.getenv("API_KEY")
    }
    try:
        response = requests.get(semantic_url, params=params, headers=headers, timeout=30)
        return response
    except requests.RequestException as e:
        print(f"Error fetching Semantic Scholar articles: {e}")
        return None

def handle_result_semantic_scholar(source, user_id):
    results = source.get("data",[])
    if not results:
        print("Semantic Scholar: no results found")
        return
    for res in results:
        id = res["paperId"]
        title = res["title"]
        abstract = res["abstract"]
        data = f"{title} {abstract}"
        cleaned_data = clean_data(data)
        embedding = get_embedding(cleaned_data)
        store_embedding_in_db(id, embedding, user_id)
        insert_article(id, title, abstract, user_id, "Semantic Scholar")



#----------------- Clinical Trials ------------------
def clinical_trials_search(query, min_date, max_date):
    q = (
    f'{query} AND AREA[StartDate]RANGE[{min_date},{max_date}]'
    )
    params = {
    "query.term": q,
    "sort": "StartDate:desc",
    "pageSize": 100
    }
    try:
        response = requests.get(clinical_trials_url, params=params, timeout=30)
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching Clinical Trials articles: {e}")
        return None

def handle_response_clinical_trials(result,user_id):

    results = result.get("studies",[])
    if not results:
        print("Clinical Trials: no results found")
        return

    for res in results:
        identification = res["protocolSection"]["identificationModule"]

        study_id = identification.get("nctId")

        title = identification.get("officialTitle", "")

        description = res["protocolSection"].get(
            "descriptionModule", {}
        ).get("detailedDescription", "")

        keyword_list = res["protocolSection"].get(
            "conditionsModule", {}
        ).get("keywords", [])
        full_keywords = " ".join(keyword_list)
        text_to_embed = f"{title} {full_keywords} {description}"
        cleaned_data = clean_data(text_to_embed)
        embedding = get_embedding(cleaned_data)
        store_embedding_in_db(study_id, embedding, user_id)
        insert_article(study_id, title, description, user_id, "ClinicalTrials")
        insert_keywords(keyword_list, study_id)
