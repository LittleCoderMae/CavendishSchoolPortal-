# test_models.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import db
from models.user import User

# Test if User model can be imported and instantiated
try:
    user = User(username='test', email='test@test.com', password_hash='test', role='student')
    print("✓ User model works!")
    print(f"✓ User: {user}")
except Exception as e:
    print(f"✗ Error with User model: {e}")