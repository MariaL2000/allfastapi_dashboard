
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import SessionLocal, engine, Base # Importamos Base de session
from models import Role, User, UserRole # Importamos el archivo de modelos y la clase Role
from core.security import pwd_context

def init_db():
    print(f"Conectando a base de datos en: {engine.url}")
    # IMPORTANTE: Esto crea las tablas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Crear Rol Admin
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Rol 'admin' creado.")

        # 2. Crear Usuario Admin
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            hashed = pwd_context.hash("admin123")
            admin_user = User(
                name="Admin User",
                email="admin@example.com",
                hashed_password=hashed,
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Usuario admin creado.")

        # 3. Asignar Rol
        link = db.query(UserRole).filter(UserRole.user_id == admin_user.id).first()
        if not link:
            db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            db.commit()
            print("Rol asignado al admin.")

    finally:
        db.close()
    print("Inicialización completa.")

if __name__ == "__main__":
    init_db()