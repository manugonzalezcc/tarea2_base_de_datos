import sys, os
# Ensure project root is on sys.path when running via uv/python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.db import sqlalchemy_config
from app.repositories.user import UserRepository, password_hasher
from app.models import User

USERNAME = "bootstrap_user"
PASSWORD = "MiPassInicial123"
FULLNAME = "Usuario Inicial"

if __name__ == "__main__":
    with sqlalchemy_config.get_session() as session:
        repo = UserRepository(session=session, auto_commit=True)
        existing = repo.get_one_or_none(username=USERNAME)
        if existing:
            print(f"Usuario ya existe: {existing.username}")
        else:
            user = User(
                username=USERNAME,
                fullname=FULLNAME,
                password=password_hasher.hash(PASSWORD),
            )
            repo.add(user)
            print(f"Usuario creado: {USERNAME}")
