from app.database import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.utils.security import get_password_hash

def seed_database():
    db = SessionLocal()
    try:
        demo_user = User(
            email="demo@example.com",
            hashed_password=get_password_hash("Demo1234")
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        demo_account = Account(
            user_id=demo_user.id,
            capital=1000.0,
            payout=0.85
        )
        db.add(demo_account)
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("Demo user: demo@example.com / Demo1234")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()