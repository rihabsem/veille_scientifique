import os
from app.data_cleaning import clean_data, get_embedding
from app.vector_db_creation import store_user_in_db
from app.model import insert_query, delete_queries_by_source, count_queries
from mistralai.client import Mistral
import json
from json_repair import repair_json
import re
import csv
from datetime import datetime
from pathlib import Path
from langdetect import detect

LOG_FILE = "mistral_usage.csv"

if not Path(LOG_FILE).exists():
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "nom_fonction",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens"
        ])

LANG_MAP = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
}

MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-2603")

PROFILE_REFINEMENT_PROMPT = """
ROLE:
You are a medical research assistant specialized in scientific literature monitoring across all areas of medicine and biomedical sciences.

TASK:
Generate exactly 1 profile-clarification question to refine a researcher's scientific literature monitoring preferences — not scientific exam questions.

CONTEXT:
{context}

INSTRUCTIONS:
{followup_instruction}  - Questions must be simple, direct, and user-oriented, focused on preferences, interests, and scope of monitoring
  - Each question must include EXACTLY 3 answer options, written inline in this exact format:
    Question text (answer 1, answer 2, answer 3)
  - Do NOT ask questions requiring specialized scientific knowledge (e.g. choosing between mechanisms, pathophysiological pathways, or methodological approaches)
  - Do NOT ask yes/no inclusion questions about narrow subtopics (e.g. "Do you want to include clinical trials on X?")
  - Do NOT ask about recency or study type preference (e.g. clinical trials vs. meta-analyses vs. case reports)
  - Do NOT mention tools, platforms (PubMed, ClinicalTrials.gov, Google Scholar, etc.), search strategies, or the technical workflow of literature monitoring
  - No explanations — output only the result.

OUTPUT LANGUAGE: {output_language}
Write the entire output — every question and every answer option — strictly in {output_language}. This is a hard requirement, not a suggestion.

OUTPUT FORMAT:
Return ONLY a string, formatted as:
"Question text (answer 1, answer 2, answer 3)"
"""


def profile_refinement(user_profile, previous_answers=None):
    """
    Generates one profile-clarification question.
    previous_answers: list of prior user answers (empty/None for the first question).
    """
    previous_answers = previous_answers or []

    detected_code = detect(user_profile)
    output_language = LANG_MAP.get(detected_code, "English")

    context = "\n".join([user_profile] + previous_answers)

    followup_instruction = (
        "  - Using the user's profile and their previous answer(s), generate a "
        "follow-up question to further refine their scientific literature "
        "monitoring preferences.\n"
        if previous_answers
        else ""
    )

    query = PROFILE_REFINEMENT_PROMPT.format(
        context=context,
        followup_instruction=followup_instruction,
        output_language=output_language,
    )

    client = Mistral(api_key=os.getenv("MISTRAL_KEY"))
    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=[{"role": "user", "content": query}],
    )

    usage = response.usage
    csv_writer(usage, "profile refinement")

    return response.choices[0].message.content.strip()



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
  - Combine AT MOST 2 core concepts with + (AND). Use | (OR) freely for synonyms within a concept.

  PUBMED FORMAT:
  - Use Boolean operators AND, OR, NOT only.
  - HARD LIMIT: use AT MOST 1 single "AND" per query, connecting exactly 2 concepts. Never chain 3 or more AND conditions.
  - Each concept can itself be a group of synonyms joined with OR, e.g. ("term1" OR "term2") AND ("term3" OR "term4") — this still counts as ONE AND.
  - Prefer a single specific concept alone over combining unrelated ones.
  - Use quotation marks for multi-word concepts.
  - The query must be short and directly usable in PubMed.

  CLINICALTRIALS QUERY FORMAT:
  - Generate a short keyword-based search query.
  - Use 3 to 6 keywords maximum, focused on ONE core concept (plus at most one qualifier).
  - No full sentences or natural language descriptions.
  - Avoid words like "studies", "research on", "applications of".
  - Focus only on medical concepts and techniques.
  - Use spaces between keywords (no Boolean operators unless necessary).

  RULES:
  - PRIORITIZE BREADTH OVER SPECIFICITY: a simpler query that returns more results is always better than a precise query that returns none.
  - Each of the 5 queries should focus on ONE distinct concept or technology from the profile, not a combination of several.
  - Do NOT combine more than 2 concepts per query, in any database format.
  - Use OR to broaden within a single concept (synonyms, related terms), never to combine unrelated concepts.
  - Generate only queries relevant to the user's interests.
  - Include synonyms when useful, to increase the chance of matches.
  - Avoid duplicate or nearly identical queries.
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
  RULES:
  - PRIORITIZE BREADTH OVER SPECIFICITY: a simpler query that returns more results is always better than a precise query that returns none.
  - Each of the 5 queries should focus on ONE distinct concept or technology from the profile, not a combination of several.
  - Do NOT combine more than 2 concepts per query, in any database format.
  - Use OR to broaden within a single concept (synonyms, related terms), never to combine unrelated concepts.
  - Generate only queries relevant to the user's interests.
  - Include synonyms when useful, to increase the chance of matches.
  - Avoid duplicate or nearly identical queries.
  - Do not explain your reasoning.
  - Do not give keywords consistent of one word only, except for acronyms or abbreviations.
  - MANDATORY: the output array MUST contain EXACTLY 5 elements, no more, no less.
  - If the profile does not offer 5 clearly distinct concepts, reuse or slightly vary secondary aspects, sub-technologies, populations, or methodologies already mentioned to reach exactly 5 queries. Never return fewer than 5.
  """
  client = Mistral(api_key=os.environ["MISTRAL_KEY"])
  response = client.chat.complete(
      model="mistral-small-2603",
      messages=[
          {"role":"user", "content":query}
      ],
  )
  usage = response.usage
  csv_writer(usage, "query generation")
  print(response.choices[0].message.content)
  return response.choices[0].message.content

def user_profile_treatment(user_profile, user_id):
  user_profile = clean_data(user_profile)
  user_embedding = get_embedding(user_profile)
  store_user_in_db(user_id, user_embedding)
  


def launch_LLM(user_profile, id_user, responses):
    res = query_generation(user_profile, responses)
    res = re.sub(r"```json|```", "", res).strip()
    try:
        res = json.loads(res)
    except json.JSONDecodeError:
        res = json.loads(repair_json(res))

    has_entries = count_queries(id_user) > 0

    for r in res:
        if has_entries:
          delete_queries_by_source(id_user)
        insert_query(r["semantic_scholar"], "Semantic Scholar", id_user)
        insert_query(r["pubmed"], "PubMed", id_user)
        insert_query(r["clinical_trials"], "Clinical Trials", id_user)

def csv_writer(usage, function_name):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            function_name,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens
        ])
if __name__ == "__main__":
  my_dic={}
  user_profile = """ Interne en cardiologie, intéressée par l'insuffisance cardiaque, les biomarqueurs cardiovasculaires et les nouvelles thérapies anticoagulantes."""
  question1 = profile_refinement(user_profile)
  print(f"Question 1: {question1}", flush=True)
  answer1 = input(f"")
  my_dic[question1] = answer1
  question2 = profile_refinement(user_profile, [answer1])
  print(f"Question 2: {question2}", flush=True)
  answer2 = input(f"")
  my_dic[question2] = answer2
  question3 = profile_refinement(user_profile, [answer1, answer2])
  print(f"Question 3: {question3}", flush=True)
  answer3 = input(f"")
  my_dic[question3] = answer3