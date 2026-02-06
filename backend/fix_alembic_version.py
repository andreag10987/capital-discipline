# fix_alembic_version.py
from app.database import engine
from sqlalchemy import text

with engine.connect() as connection:
    # Ver versión actual
    result = connection.execute(text("SELECT version_num FROM alembic_version"))
    current_version = result.fetchone()
    print(f"Versión actual: {current_version[0] if current_version else 'Ninguna'}")
    
    # Actualizar a 009_add_admin_role (la última)
    connection.execute(text("DELETE FROM alembic_version"))
    connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('009_add_admin_role')"))
    connection.commit()
    
    # Verificar
    result = connection.execute(text("SELECT version_num FROM alembic_version"))
    new_version = result.fetchone()
    print(f"Nueva versión: {new_version[0]}")
    print("✅ Alembic version actualizada a 009")