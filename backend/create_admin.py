# create_admin.py
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
from app.services.plan_service import assign_free_plan_to_new_user
from datetime import datetime

EMAIL = "admin@example.com"
PASSWORD = "admin123"

db = SessionLocal()

# Verificar si ya existe
existing = db.query(User).filter(User.email == EMAIL).first()
if existing:
    # Si existe, solo hacerlo admin
    existing.is_admin = True
    db.commit()
    print(f"✅ Usuario {EMAIL} actualizado a admin")
    db.close()
    exit()

# Crear usuario admin nuevo
new_user = User(
    email=EMAIL,
    hashed_password=get_password_hash(PASSWORD),
    email_verified=True,
    is_admin=True,
    created_at=datetime.utcnow()
)

db.add(new_user)
db.flush()

# Asignar plan FREE
assign_free_plan_to_new_user(db, new_user.id)

db.commit()
print(f"✅ Usuario admin creado:")
print(f"   Email: {EMAIL}")
print(f"   Password: {PASSWORD}")
print(f"   Puedes cambiar el password después")
db.close()