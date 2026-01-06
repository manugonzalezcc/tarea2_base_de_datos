import sys, os
# Ensure project root is on sys.path when running via uv/python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.db import sqlalchemy_config
from app.repositories.user import UserRepository, password_hasher
from app.models import User

USERNAME = os.getenv("BOOTSTRAP_USERNAME", "bootstrap_user")
PASSWORD = os.getenv("BOOTSTRAP_PASSWORD", "MiPassInicial123")
FULLNAME = os.getenv("BOOTSTRAP_FULLNAME", "Usuario Inicial")
EMAIL = os.getenv("BOOTSTRAP_EMAIL", "bootstrap_user@example.com")

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
                email=EMAIL,
                password=password_hasher.hash(PASSWORD),
            )
            repo.add(user)
            print(f"Usuario creado: {USERNAME}")
