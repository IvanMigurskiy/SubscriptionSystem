from passlib.context import CryptContext


class PasswordEngine:
    CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordEngine.CONTEXT.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return PasswordEngine.CONTEXT.verify(plain_password, hashed_password)
