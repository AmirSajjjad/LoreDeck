from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


class PasswordService:
    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()
        self._dummy_hash = self._password_hash.hash("dummy-password-used-only-for-timing")

    def hash_password(self, plain_password: str) -> str:
        return self._password_hash.hash(plain_password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        try:
            return self._password_hash.verify(plain_password, password_hash)
        except (TypeError, ValueError, UnknownHashError):
            return False

    def verify_dummy_password(self, plain_password: str) -> None:
        self.verify_password(plain_password, self._dummy_hash)
