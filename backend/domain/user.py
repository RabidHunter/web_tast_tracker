from typing import Optional


class User:
    def __init__(self, id: Optional[int], username: str, password_hash: str):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password_to_check: str) -> bool:
        return False
