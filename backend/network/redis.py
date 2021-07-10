from walrus import Walrus

from backend.network.database import Database, FacialData


class RedisDB(Database):
    def get_landmarks(self, image_hash: str) -> FacialData:
        pass

    def save_landmarks(self, data: FacialData) -> str:
        db = Walrus(host='localhost', port=6379, db=0)