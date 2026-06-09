from src.utils.db_utils import get_db_connection


class SingerIdLinker:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def link_embedding_to_vocalist(self, embedding_id: str, vocalist_id: str):
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE embeddings SET vocalist_id = ? WHERE id = ?", (vocalist_id, embedding_id)
            )
            return cursor.rowcount > 0
