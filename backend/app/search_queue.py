from queue import Queue
from threading import Thread
from app.database import SessionLocal
from app.model import get_user_by_id
from app.coord import first_search


search_queue = Queue()


def worker():
    """
    Traite les recherches une par une.
    """
    while True:

        user_id = search_queue.get()

        try:
            print(f"Début recherche utilisateur {user_id}")

            db = SessionLocal()

            try:
                user = get_user_by_id(user_id)

                if user:
                    first_search(db, user)

            finally:
                db.close()

            print(f"Recherche terminée utilisateur {user_id}")

        except Exception as e:
            print(
                f"Erreur recherche utilisateur {user_id}: {e}"
            )

        finally:
            search_queue.task_done()


worker_thread = Thread(
    target=worker,
    daemon=True
)

worker_thread.start()