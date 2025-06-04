from typing import List
from supabase import create_client, Client


class HighscoreManager:
    def __init__(self, url: str, key: str):
        if url and key:
            self.client: Client = create_client(url, key)
        else:
            self.client = None

    def get_highscores(self) -> List[dict]:
        """Fetch top 10 highscores."""
        if not self.client:
            return []
        response = (
            self.client.table('highscores')
            .select('name, score')
            .order('score', desc=True)
            .limit(10)
            .execute()
        )
        return response.data if response.data else []

    def record_highscore(self, name: str, score: int) -> None:
        """Insert a new highscore."""
        if not self.client:
            return
        self.client.table('highscores').insert({'name': name, 'score': score}).execute()
