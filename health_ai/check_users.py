import sys
sys.path.insert(0, ".")
from app import create_app
app = create_app()
with app.app_context():
    from models import User
    users = User.query.all()
    if not users:
        print("NO USERS IN DATABASE")
    for u in users:
        print(f"  [{u.role}] {u.email} | active={u.is_active}")
