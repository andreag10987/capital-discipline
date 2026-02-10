import argparse
from datetime import datetime

from app.database import SessionLocal
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.security import get_password_hash


def grant_full_access(email: str, password: str | None) -> None:
    db = SessionLocal()
    try:
        normalized_email = email.strip().lower()
        now = datetime.utcnow()

        user = db.query(User).filter(User.email == normalized_email).first()
        created = False

        if not user:
            if not password:
                raise ValueError("Password is required when creating a new user.")
            user = User(
                email=normalized_email,
                hashed_password=get_password_hash(password),
                email_verified=True,
                is_admin=True,
                is_blocked=False,
                blocked_reason=None,
                blocked_at=None,
                created_at=now,
            )
            db.add(user)
            db.flush()
            created = True
        else:
            if password:
                user.hashed_password = get_password_hash(password)
            user.email_verified = True
            user.is_admin = True
            user.is_blocked = False
            user.blocked_reason = None
            user.blocked_at = None

        pro_plan = (
            db.query(Plan)
            .filter(Plan.name == "PRO", Plan.is_active == True)
            .first()
        )

        if not pro_plan:
            pro_plan = (
                db.query(Plan)
                .filter(Plan.is_active == True)
                .order_by(Plan.price_usd.desc())
                .first()
            )

        if not pro_plan:
            raise ValueError("No active plans found in database.")

        db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "ACTIVE",
        ).update(
            {
                Subscription.status: "CANCELED",
                Subscription.updated_at: now,
            },
            synchronize_session=False,
        )

        subscription = Subscription(
            user_id=user.id,
            plan_id=pro_plan.id,
            status="ACTIVE",
            start_date=now,
            end_date=None,
            payment_provider="manual_admin",
            external_subscription_id=None,
            created_at=now,
            updated_at=now,
        )
        db.add(subscription)
        db.commit()

        print("OK: full access granted")
        print(f"user_id={user.id}")
        print(f"email={user.email}")
        print(f"created={created}")
        print(f"is_admin={user.is_admin}")
        print(f"is_blocked={user.is_blocked}")
        print(f"plan={pro_plan.name}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Grant full app access to a user.")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument(
        "--password",
        required=False,
        default=None,
        help="Optional password to set/reset for this user",
    )
    args = parser.parse_args()

    grant_full_access(args.email, args.password)


if __name__ == "__main__":
    main()
