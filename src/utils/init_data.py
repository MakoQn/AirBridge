from src.database.db_connection import SessionLocal
from src.database.models.auth import Role, AppUser
import bcrypt

def init_roles_and_admin():
    session = SessionLocal()
    try:
        roles = ["Administrator", "Dispatcher", "Client"]
        for r_name in roles:
            existing = session.query(Role).filter_by(role_name=r_name).first()
            if not existing:
                new_role = Role(role_name=r_name, role_description=f"Role for {r_name}")
                session.add(new_role)
        
        session.commit()

        admin_user = session.query(AppUser).filter_by(username="admin").first()
        if not admin_user:
            admin_role = session.query(Role).filter_by(role_name="Administrator").first()
            password_bytes = "admin123".encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

            new_admin = AppUser(
                username="admin",
                email="admin@airbridge.loc",
                password_hash=hashed
            )
            new_admin.roles.append(admin_role)
            session.add(new_admin)
            session.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_roles_and_admin()