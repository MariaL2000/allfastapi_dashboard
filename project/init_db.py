import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from db.session import SessionLocal, engine, Base
from models.models import Role, User, UserRole
from core.security import get_password_hash

def init_db():
    print(f"--- Iniciando base de datos en: {engine.url} ---")
    
    # 1. Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 2. Crear Roles Base
        roles_to_create = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "user", "description": "Standard customer/user access"}
        ]

        created_roles = {}
        for r_data in roles_to_create:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                role = Role(name=r_data["name"], description=r_data["description"])
                db.add(role)
                db.commit()
                db.refresh(role)
                print(f"✅ Rol '{r_data['name']}' creado.")
            created_roles[r_data["name"]] = role

        # 3. Crear Superusuario Inicial
        admin_email = "admin@example.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_user:
            admin_user = User(
                name="Super Admin",
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Usuario Admin creado ({admin_email}).")

            # 4. Asignar Rol Admin al Superusuario
            user_role_link = UserRole(user_id=admin_user.id, role_id=created_roles["admin"].id)
            db.add(user_role_link)
            db.commit()
            print("✅ Rol 'admin' asignado al usuario administrador.")
        else:
            print("ℹ️ El usuario administrador ya existe.")

    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        db.rollback()
    finally:
        db.close()
        print("--- Proceso de inicialización finalizado ---")

if __name__ == "__main__":
    init_db()