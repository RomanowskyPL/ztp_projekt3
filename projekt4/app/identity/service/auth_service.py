from datetime import datetime, timedelta
import secrets

from sqlalchemy.orm import Session

from app.identity.data.operator_repository import (
    get_operator_by_email,
    get_operator_by_id,
    create_operator,
)
from app.identity.data.session_repository import (
    get_session_by_token,
    delete_session_by_id,
    create_session,
    update_session_last_used,
)
from app.identity.model.operator_orm import OperatorORM
from app.identity.service.password_hasher import hash_password, verify_password
from app.identity.service.auth_validators import validate_password_strength, ValidationError


SESSION_MAX_AGE_SECONDS = 1800


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


def is_session_expired(last_used_at: datetime) -> bool:
    return datetime.now() - last_used_at > timedelta(seconds=SESSION_MAX_AGE_SECONDS)


def register_operator(db: Session, email: str, password: str, confirm_password: str, first_name: str, last_name: str):
    if password != confirm_password:
        raise ValidationError("Hasła nie są takie same.")

    validate_password_strength(password)

    existing = get_operator_by_email(db, email)
    if existing:
        raise ValidationError("Operator z takim emailem już istnieje.")

    operator = OperatorORM(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    return create_operator(db, operator)


def login_operator(db: Session, email: str, password: str):
    operator = get_operator_by_email(db, email)
    if operator is None:
        raise AuthenticationError("Niepoprawny email lub hasło.")

    if not operator.is_active:
        raise AuthorizationError("Konto jest nieaktywne.")

    if not verify_password(password, operator.password_hash):
        raise AuthenticationError("Niepoprawny email lub hasło.")

    token = secrets.token_hex(32)
    create_session(db, operator.id, token)

    return operator, token


def logout_operator(db: Session, token: str):
    session = get_session_by_token(db, token)
    if session:
        delete_session_by_id(db, session.id)


def get_current_operator(db: Session, token: str) -> OperatorORM:
    session = get_session_by_token(db, token)
    if session is None:
        raise AuthorizationError("Brak aktywnej sesji.")

    if is_session_expired(session.last_used_at):
        delete_session_by_id(db, session.id)
        raise AuthorizationError("Sesja wygasła.")

    operator = get_operator_by_id(db, session.operator_id)
    if operator is None:
        delete_session_by_id(db, session.id)
        raise AuthorizationError("Operator nie istnieje.")

    if not operator.is_active:
        delete_session_by_id(db, session.id)
        raise AuthorizationError("Konto nieaktywne.")

    update_session_last_used(db, session)
    return operator