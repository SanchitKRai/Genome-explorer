"""Shared domain error exception for consistent { error: { code, message } } responses."""


class AppError(Exception):
    """Domain exception producing consistent { error: { code, message } } responses."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
