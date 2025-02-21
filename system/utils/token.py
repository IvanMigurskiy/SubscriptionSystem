import os

from jose import jwt
from datetime import datetime, timedelta


class TokenEngine:
    SECRET_KEY = os.environ.get('TOKEN_SECRET_KEY', '')
    TTL = int(os.environ.get('COOKIE_TTL_MINUTES', '60'))
    ALGORITHM = 'HS256'

    @staticmethod
    def create_access_token(mail: str):
        data = {'mail': mail, 'exp': datetime.utcnow() + timedelta(minutes=TokenEngine.TTL)}
        return jwt.encode(data, TokenEngine.SECRET_KEY, algorithm=TokenEngine.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> tuple[bool, str]:
        try:
            payload = jwt.decode(token, TokenEngine.SECRET_KEY, algorithms=[TokenEngine.ALGORITHM])
            if payload['exp'] < datetime.utcnow().timestamp():
                return False, ''
            return True, payload['mail']
        except Exception:
            return False, ''
