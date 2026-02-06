# create_admin_simple.py
from app.database import SessionLocal
from app.models.user import User
from app.services.plan_service import assign_free_plan_to_new_user
from datetime import datetime
import bcrypt

EMAIL = "admin@example.com"
PASSWORD = "admin123"

db = SessionLocal()

# Verificar si ya existe
existing = db.query(User).filter(User.email == EMAIL).first()
if existing:
    existing.is_admin = True
    db.commit()
    print(f"✅ Usuario {EMAIL} actualizado a admin")
    db.close()
    exit()

# Hash del password manualmente con bcrypt
password_bytes = PASSWORD.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)

# Crear usuario
new_user = User(
    email=EMAIL,
    hashed_password=hashed.decode('utf-8'),
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
db.close()