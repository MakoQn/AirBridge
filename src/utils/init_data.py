from src.database.db_connection import SessionLocal
from src.database.models.auth import Role, AppUser
import bcrypt

def init_system():
    session = SessionLocal()
    try:
        roles = ["Administrator", "Dispatcher", "Client"]
        for r_name in roles:
            if not session.query(Role).filter_by(role_name=r_name).first():
                session.add(Role(role_name=r_name, role_description=f"Role for {r_name}"))
        session.commit()

        if not session.query(AppUser).filter_by(username="admin").first():
            pwd = "admin".encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(pwd, salt).decode('utf-8')

            superuser = AppUser(
                username="admin", 
                email="root@system.loc", 
                password_hash=hashed,
                is_superuser=True
            )
            session.add(superuser)
            session.commit()
            print("Superuser created (admin/admin)")
        else:
            print("Superuser exists")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_system()