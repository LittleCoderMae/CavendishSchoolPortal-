# database/__init__.py
from .database import db, login_manager, init_db

__all__ = ['db', 'login_manager', 'init_db']