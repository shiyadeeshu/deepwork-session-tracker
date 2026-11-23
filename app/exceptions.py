"""Domain errors raised by the service layer and mapped to HTTP responses."""


class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class SessionNotFoundError(DomainError):
    status_code = 404

    def __init__(self, session_id: int):
        super().__init__(f"Session {session_id} not found")


class InvalidStateTransitionError(DomainError):
    status_code = 409

    def __init__(self, action: str, current: str, allowed: list[str]):
        super().__init__(
            f"Cannot {action} a session that is '{current}'. "
            f"Allowed when: {', '.join(allowed)}"
        )
