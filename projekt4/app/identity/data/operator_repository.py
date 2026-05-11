from sqlalchemy.orm import Session

from app.identity.model.operator_orm import OperatorORM


def get_operator_by_email(db: Session, email: str) -> OperatorORM | None:
    return db.query(OperatorORM).filter(OperatorORM.email == email).first()


def get_operator_by_id(db: Session, operator_id: int) -> OperatorORM | None:
    return db.query(OperatorORM).filter(OperatorORM.id == operator_id).first()


def create_operator(db: Session, operator: OperatorORM) -> OperatorORM:
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return operator