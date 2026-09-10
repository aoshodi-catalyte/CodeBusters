from datetime import date, datetime, timedelta, timezone

from password_reset.password_reset_schema import PasswordResetToken
from employee.employee_role_schema import EmployeeRoleSchema 
from employee.employee_schema import EmployeeSchema 


def test_password_reset_token_model():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    reset_token = PasswordResetToken(
        employee_id=7,
        token_hash="hashed-token",
        expires_at=expires_at,
        channel="email",
    )

    assert reset_token.employee_id == 7
    assert reset_token.token_hash == "hashed-token"
    assert reset_token.expires_at == expires_at
    assert reset_token.used_at is None
    assert reset_token.channel == "email"

def test_password_reset_token_can_be_saved(db):
    role = (
        db.query(EmployeeRoleSchema)
        .filter(EmployeeRoleSchema.role == "manager")
        .first()
    )

    employee = EmployeeSchema(
        active=True,
        first_name="John",
        last_name="Smith",
        email="john.reset@example.com",
        phone_number="5551234567",
        role_id=role.id,
        hourly_rate=20.00,
        hire_date=date(2026, 9, 10),
    )

    db.add(employee)
    db.flush()

    reset_token = PasswordResetToken(
        employee_id=employee.id,
        token_hash="hashed-reset-code",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        channel="email",
    )

    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)

    assert reset_token.id is not None
    assert reset_token.employee_id == employee.id
    assert reset_token.channel == "email"
    assert reset_token.used_at is None
