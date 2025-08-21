# adminroles.py
from db import SessionLocal, engine
import models
from auth import pwd_context  # importamos el contexto que usa pbkdf2_sha256
import sys

def init_db():
    print("Usando DB:", str(engine.url))  # te dice la ruta absoluta del sqlite
    # Crear tablas
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Crear rol admin si no existe
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin_role:
            admin_role = models.Role(
                name="admin",
                description="Administrator role with full privileges"
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        # Crear usuario admin si no existe
        admin_user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
        if not admin_user:
            try:
                hashed = pwd_context.hash("admin123")
            except Exception as e:
                print("Error al hashear la contraseña:", e)
                raise

            admin_user = models.User(
                name="Admin User",
                email="admin@example.com",
                hashed_password=hashed,
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Asignar rol admin al usuario
            user_role = models.UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id
            )
            db.add(user_role)
            db.commit()
        else:
            # si ya existe el usuario, aseguramos la relación con el rol admin
            ur = db.query(models.UserRole).filter(
                models.UserRole.user_id == admin_user.id,
                models.UserRole.role_id == admin_role.id
            ).first()
            if not ur:
                user_role = models.UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
                db.add(user_role)
                db.commit()

    finally:
        db.close()
    print("init_db completado.")

if __name__ == "__main__":
    init_db()
