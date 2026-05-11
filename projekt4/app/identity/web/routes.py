from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlalchemy.orm import Session

from app.REST.data.database import get_db
from app.identity.model.auth_schema import RegisterRequest, LoginRequest
from app.identity.model.operator_schema import OperatorResponse
from app.identity.service.auth_service import (
    register_operator,
    login_operator,
    logout_operator,
    get_current_operator,
    SESSION_MAX_AGE_SECONDS,
    AuthenticationError,
    AuthorizationError,
)
from app.identity.service.auth_validators import ValidationError

router = APIRouter(tags=["Identity"])


@router.post("/auth/register", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
def register_endpoint(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        operator = register_operator(
            db=db,
            email=payload.email,
            password=payload.password,
            confirm_password=payload.confirm_password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        return operator
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/auth/login", response_model=OperatorResponse)
def login_endpoint(
    payload: LoginRequest,
    response: Response,
    auth_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    try:
        if auth_token is not None:
            logout_operator(db, auth_token)

        operator, token = login_operator(db, payload.email, payload.password)

        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=SESSION_MAX_AGE_SECONDS,
        )

        return operator

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))

    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/auth/me", response_model=OperatorResponse)
def me_endpoint(
    response: Response,
    auth_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if auth_token is None:
        raise HTTPException(status_code=401, detail="Brak aktywnej sesji.")

    try:
        operator = get_current_operator(db, auth_token)

        response.set_cookie(
            key="auth_token",
            value=auth_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=SESSION_MAX_AGE_SECONDS,
        )

        return operator

    except AuthorizationError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_endpoint(
    response: Response,
    auth_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if auth_token is not None:
        logout_operator(db, auth_token)

    response.delete_cookie(
        key="auth_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    response.status_code = 204
    return response