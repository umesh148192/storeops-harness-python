from __future__ import annotations


class AppError(Exception):
    code: str
    message: str
    status_code: int

    def __init__(self, message: str, *, code: str | None = None, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, code="CONFLICT", status_code=409)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401)
