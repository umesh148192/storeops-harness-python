from __future__ import annotations

from storeops.shared.errors import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def test_app_error_defaults_status_code():
    error = AppError("boom")
    assert error.message == "boom"
    assert error.code == "AppError"
    assert error.status_code == 500


def test_app_error_custom_code_and_status():
    error = AppError("boom", code="CUSTOM", status_code=418)
    assert error.code == "CUSTOM"
    assert error.status_code == 418


def test_not_found_error():
    error = NotFoundError("missing")
    assert error.status_code == 404
    assert error.code == "NOT_FOUND"


def test_validation_error():
    error = ValidationError()
    assert error.status_code == 422


def test_forbidden_error():
    error = ForbiddenError()
    assert error.status_code == 403


def test_conflict_error():
    error = ConflictError()
    assert error.status_code == 409


def test_unauthorized_error():
    error = UnauthorizedError()
    assert error.status_code == 401
