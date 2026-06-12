from typing import Any, Dict
from fastapi import HTTPException, status


class SSHManagerException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class EntityNotFoundException(SSHManagerException):
    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with id {entity_id} not found",
        )


class EntityAlreadyExistsException(SSHManagerException):
    def __init__(self, entity_name: str, field_name: str, value: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_name} with {field_name} '{value}' already exists",
        )


class InvalidCredentialsException(SSHManagerException):
    def __init__(self, detail: str = "Incorrect username or password") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(SSHManagerException):
    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class SSHConnectionException(SSHManagerException):
    def __init__(self, server_name: str, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to server '{server_name}': {detail}",
        )


class BusinessRuleException(SSHManagerException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
