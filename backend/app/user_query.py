import os
from app.data_cleaning import clean_data, get_embedding
from app.vector_db_creation import store_user_in_db
from app.model import insert_query
from mistralai.client import Mistral
import json
from json_repair import repair_json
import re

#1_ clean the data
# 2_ send the query to the api

def profile_refinement(user_profile):
  query = f"""
  ROLE:
  You are a medical research assistant specialized in scientific literature monitoring across all areas of medicine and biomedical sciences.

  TASK:
  Generate questions to refine a researcher's scientific knowledge profile.

  CONTEXT:
  {user_profile}

  INSTRUCTIONS:
  - Based on the user's profile, generate exactly 3 questions
  - These questions are NOT scientific exam questions
  - They are profile clarification questions
  - Their goal is to better understand what the user wants to monitor in medical literature

  - Questions should be simple, direct, and user-oriented
  - Focus on preferences, interests, and scope of monitoring

  Examples of good questions (non-exhaustive):
  - Which medical specialties are most relevant to your work or interest?
  - Are you more interested in diagnosis, treatment, or disease mechanisms?

  - Do NOT generate advanced scientific or research-review style questions
  - Do NOT ask questions that require specialized scientific knowledge to answer (e.g. choosing between specific mechanisms, pathophysiological pathways, or methodological approaches)
  - Do NOT ask yes/no questions about whether to "include" a specific narrow subtopic (e.g. "Do you want to include clinical trials on X?")
  - Do NOOT ask the user if they are interested in recent or old literature, or if they want to focus on specific study types (e.g. clinical trials, meta-analyses, case reports)

  - Questions must NOT include:
    - tools or platforms (PubMed, ClinicalTrials, Google Scholar, etc.)
    - search strategies
    - technical workflow of literature monitoring
  - Do not provide explanations

  IMPORTANT:
  - The output language MUST strictly match the language of the input profile
  - Do NOT translate
  - Do NOT change language

  OUTPUT FORMAT:
  Return ONLY a JSON array of 3 strings
  """
  client = Mistral(api_key=os.getenv("MISTRAL_KEY"))
  response = client.chat.complete(
      model="mistral-small-2603",
      messages=[
          {"role":"user", "content":query}
      ],
  )
  questions = response.choices[0].message.content
  questions = re.sub(r"```json|```","",questions).strip()
  questions = json.loads(questions)
  return questions

def  query_generation(user_profile, user_answers):
  query = f"""
  ROLE:
  You are an expert in biomedical information retrieval and scientific literature monitoring.

  TASK:
  Generate optimized search queries for scientific databases based on a user's profile and their answers to refinement questions.

  INPUT:

  User profile:
  {user_profile}

  User answers:
  {user_answers}

  INSTRUCTIONS:

  - The user answers are provided in the format:
    Question: Answer

  - Analyze both the user profile and the answers.

  - Generate up to 5 distinct search queries.

  - Each query should target a different aspect, subtopic, methodology, population, disease, technology, or research objective mentioned by the user.

  - For each generated query, provide the equivalent formulation for:
    1. Semantic Scholar
    2. PubMed
    3. ClinicalTrials.gov

  SEMANTIC SCHOLAR FORMAT:
  Use the following syntax when appropriate:
  - + for AND
  - | for OR
  - - for NOT
  - "..." for exact phrases
  - (...) for grouping
  - * for prefixes

  PUBMED FORMAT:
  - Use Boolean operators AND, OR, NOT.
  - Use Boolean operators ONLY DONT add any other operator.
  The query should be as simple as possible, not nested or complex, and composed of basic keywords separated by Boolean operators.
  - Use quotation marks for multi-word concepts when appropriate.
  - Produce queries directly usable in PubMed.

  CLINICALTRIALS QUERY FORMAT:
  - Generate a short keyword-based search query.
  - Use 3 to 8 keywords maximum.
  - No full sentences or natural language descriptions.
  - Avoid words like "studies", "research on", "applications of".
  - Focus only on medical concepts and techniques.
  - Use spaces between keywords (no Boolean operators unless necessary).
  - Prioritize clinical terms, diseases, methods, and data types.

  RULES:
  - Generate only queries relevant to the user's interests.
  - Include synonyms when useful.
  - Avoid duplicate or nearly identical queries.
  - Balance specificity and coverage.
  - Do not explain your reasoning.
  - Do not give keywords consistent of one word only, except for acronyms or abbreviations.

  OUTPUT FORMAT:
  Return ONLY a JSON array.
  The response must be directly parsable by Python json.loads().

  IMPORTANT:
  - Return valid JSON only.
  - Every value must be a JSON string.
  - Return valid, standard JSON with double quotes for all keys and string values
  - Do not use markdown.
  - Do not wrap the output in ```json.
  - You MUST reply with the same language as the input.

Each element must be a dictionary with the following structure:

{{
  "id": integer,
  "semantic_scholar": string,
  "pubmed": string,
  "clinical_trials": string
}}

RULES:
- Do not include explanations
- Do not include markdown
- Do not duplicate queries
- Ensure diversity across queries
- Maximum 5 queries
  """
  client = Mistral(api_key=os.environ["MISTRAL_KEY"])
  response = client.chat.complete(
      model="mistral-small-2603",
      messages=[
          {"role":"user", "content":query}
      ],
  )
  return response.choices[0].message.content

def user_profile_treatment(user_profile, user_id):
  user_profile = clean_data(user_profile)
  user_embedding = get_embedding(user_profile)
  store_user_in_db(user_id, user_embedding)
  



def launch_LLM(user_profile, id_user, responses):
  res = query_generation(user_profile, responses)
  res = re.sub(r"```json|```","",res).strip()
  try:
    res = json.loads(res)
  except json.JSONDecodeError:
    res = json.loads(repair_json(res))
  print(res)
  # res = json.loads(res)
  for r in res:
    insert_query(r["semantic_scholar"], "Semantic Scholar", id_user)
    insert_query(r["pubmed"], "PubMed", id_user)
    insert_query(r["clinical_trials"], "Clinical Trials", id_user)

  

if __name__ == "__main__":
  responses=[]
  user_profile = """ Interne en cardiologie, intéressée par l'insuffisance cardiaque, les biomarqueurs cardiovasculaires et les nouvelles thérapies anticoagulantes."""
  
  user_profile_treatment(user_profile,1)
  response = profile_refinement(user_profile)
  print(response)
  responses = []
  for r in response:
    print(r)
    response = input("")
    responses.append(response)

  res = query_generation(user_profile, responses)
  print(res)


#   res = """
#   [
#   {
#     "id": 1,
#     "semantic_scholar": "(chronic kidney disease OR CKD OR diabetic nephropathy OR hypertensive nephropathy OR glomerular disease) + (artificial intelligence OR machine learning OR deep learning OR predictive model*) + (electronic health record* OR EHR OR real-world data OR clinical data) + (risk stratification OR predictive analytics OR clinical decision support OR explainable AI)",
#     "pubmed": "((chronic kidney disease OR CKD OR diabetic nephropathy OR hypertensive nephropathy OR glomerular disease) AND (artificial intelligence OR machine learning OR deep learning OR predictive model*) AND (electronic health record* OR EHR OR real-world data OR clinical data) AND (risk stratification OR predictive analytics OR clinical decision support OR explainable AI))",
#     "clinical_trials": "Studies on AI applications in chronic kidney disease using electronic health records or real-world clinical data for risk stratification and predictive modeling"
#   },
#   {
#     "id": 2,
#     "semantic_scholar": "(diabetic nephropathy OR hypertensive nephropathy OR glomerular disease) + (acute kidney injury OR AKI) + (transition OR progression OR chronic kidney disease OR CKD) + (predictive model* OR machine learning OR risk stratification) + (validation OR external validation OR prospective study)",
#     "pubmed": "((diabetic nephropathy OR hypertensive nephropathy OR glomerular disease) AND (acute kidney injury OR AKI) AND (transition OR progression OR chronic kidney disease OR CKD) AND (predictive model* OR machine learning OR risk stratification) AND (validation OR external validation OR prospective study))",
#     "clinical_trials": "Clinical studies on predictive models for acute kidney injury progression to chronic kidney disease using machine learning and validation in real-world settings"
#   },
#   {
#     "id": 3,
#     "semantic_scholar": "(chronic kidney disease OR CKD) + (cardiovascular complication* OR cardiovascular disease OR mortality) + (risk prediction OR predictive model* OR machine learning) + (systematic review OR meta-analysis OR cohort study)",
#     "pubmed": "((chronic kidney disease OR CKD) AND (cardiovascular complication* OR cardiovascular disease OR mortality) AND (risk prediction OR predictive model* OR machine learning) AND (systematic review OR meta-analysis OR cohort study))",
#     "clinical_trials": "Systematic reviews and meta-analyses on cardiovascular risk prediction in chronic kidney disease using machine learning models"
#   },
#   {
#     "id": 4,
#     "semantic_scholar": "(explainable AI OR XAI OR interpretable machine learning) + (chronic kidney disease OR CKD OR nephrology) + (predictive model* OR risk stratification OR clinical decision support) + (electronic health record* OR EHR OR healthcare workflow*)",
#     "pubmed": "((explainable AI OR XAI OR interpretable machine learning) AND (chronic kidney disease OR CKD OR nephrology) AND (predictive model* OR risk stratification OR clinical decision support) AND (electronic health record* OR EHR OR healthcare workflow*))",
#     "clinical_trials": "Studies on explainable AI methods for predictive modeling in nephrology integrated into electronic health records or clinical workflows"
#   },
#   {
#     "id": 5,
#     "semantic_scholar": "(novel biomarker* OR precision medicine OR personalized medicine) + (chronic kidney disease OR CKD OR diabetic nephropathy OR hypertensive nephropathy) + (predictive model* OR risk stratification OR early intervention) + (clinical trial* OR validation study OR prospective cohort)",
#     "pubmed": "((novel biomarker* OR precision medicine OR personalized medicine) AND (chronic kidney disease OR CKD OR diabetic nephropathy OR hypertensive nephropathy) AND (predictive model* OR risk stratification OR early intervention) AND (clinical trial* OR validation study OR prospective cohort))",
#     "clinical_trials": "Clinical trials and validation studies on novel biomarkers and precision medicine approaches for chronic kidney disease with predictive modeling applications"
#   }
# ]
# """

  # try:
  #   res = json.loads(res)
  # except json.JSONDecodeError as e:
  #   print(f"Erreur ligne {e.lineno}, colonne {e.colno}")
  #   print(e)

  # for r in res:
  #   insert_query(r["semantic_scholar"], "Semantic Scholar", 1)
  #   print(r["semantic_scholar"])
  #   print("----------------------------------------------------------------")
  #   insert_query(r["pubmed"], "PubMed", 1)
  #   print(r["pubmed"])
  #   print("----------------------------------------------------------------")
  #   insert_query(r["clinical_trials"], "Clinical Trials", 1)
  #   print(r["clinical_trials"])
  #   print("----------------------------------------------------------------")
    



