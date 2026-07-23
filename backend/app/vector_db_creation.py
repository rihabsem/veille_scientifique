import chromadb
import os

_client = None
_articles_collection = None
_users_collection = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST"),
            port=int(os.getenv("CHROMA_PORT", 8000))
        )
    return _client


def get_articles_collection():
    global _articles_collection
    if _articles_collection is None:
        client = get_client()
        _articles_collection = client.get_or_create_collection("articles")
    return _articles_collection


def get_users_collection():
    global _users_collection
    if _users_collection is None:
        client = get_client()
        _users_collection = client.get_or_create_collection("users")
    return _users_collection



def store_embedding_in_db(article_id, full_embedding, user_id):
    collection = get_articles_collection()
    try:
        collection.add(
            ids=[article_id],
            embeddings=[full_embedding],
            metadatas=[{"user_id" : user_id}]
        )
        print(f"Stored : {article_id}")
    except Exception as e:
        print(f"Error storing {article_id} : {e}")

def store_user_in_db(user_id, profile_embedding):
    user_collection = get_users_collection()
    try:
        user_collection.add(
            ids=[str(user_id)],
            embeddings=[profile_embedding]
        )
        print(f"Stored : {user_id}")
    except Exception as e:
        print(f"Error storing {profile_embedding} : {e}")

def search_user_embedding(user_id):
    collection = get_users_collection()
    result = collection.get(
        ids=[str(user_id)],
        include=["embeddings"]
    )

    embeddings = result["embeddings"]

    if embeddings is None or len(embeddings) == 0:
        return None

    if embeddings[0] is None:
        return None

    return embeddings[0]


def search_articles_for_user(user_id, k=20):
    user_embedding = search_user_embedding(str(user_id))
    if user_embedding is None:
        print("No embedding found for user")
        return None

    collection = get_articles_collection()

    results = collection.query(
        query_embeddings=[user_embedding],
        n_results=k,
        where={"user_id": user_id}
    )
    return (results["ids"][0])

def delete_old_articles(user_id):
    collection = get_articles_collection()
    try:
        collection.delete(
            where={"user_id" : user_id}
        )
        print(f"Deleted articles for user {user_id}")
    except Exception as e:
        print(f"Problem deleting articles for user {user_id} : {e}")


