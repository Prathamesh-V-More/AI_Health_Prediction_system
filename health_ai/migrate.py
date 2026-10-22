import sys, os
sys.path.insert(0, ".")

from app import create_app, db
app = create_app()

with app.app_context():
    from sqlalchemy import text
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
            conn.commit()
        print("role column added")
    except Exception as e:
        print(f"Column note: {e}")

    with db.engine.connect() as conn:
        conn.execute(text("UPDATE users SET role='user' WHERE role IS NULL"))
        conn.commit()

    from models import User
    admin = User.query.filter_by(email="admin@health.com").first()
    if not admin:
        admin = User(full_name="Administrator", email="admin@health.com",
                     age=30, gender="Other", phone="0000000000", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@health.com / admin123")
    else:
        admin.role = "admin"
        db.session.commit()
        print("Admin role set.")
