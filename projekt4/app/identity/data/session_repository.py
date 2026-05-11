from datetime import datetime
from sqlalchemy.orm import Session

from app.identity.model.operator_session_orm import OperatorSessionORM


def get_session_by_token(db: Session, token: str) -> OperatorSessionORM | None:
    return db.query(OperatorSessionORM).filter(
        OperatorSessionORM.session_token == token
    ).first()


def delete_session_by_id(db: Session, session_id: int):
    session = db.query(OperatorSessionORM).filter(OperatorSessionORM.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()


def create_session(db: Session, operator_id: int, token: str) -> OperatorSessionORM:
    session = OperatorSessionORM(operator_id=operator_id, session_token=token)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session_last_used(db: Session, session: OperatorSessionORM):
    session.last_used_at = datetime.now()
    db.commit()