from app.core.observability import log_event


def audit_staff_action(action: str, *, staff_id: int, branch_id: int, success: bool) -> None:
    log_event("staff_action", action=action, staff_id=staff_id, branch_id=branch_id, success=success)


def audit_login(*, email: str, success: bool, client: str) -> None:
    log_event("staff_login", email=email, client=client, success=success)
