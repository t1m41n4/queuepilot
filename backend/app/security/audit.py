import logging


# Uvicorn configures this logger in the API container, while applications that
# embed FastAPI can still capture these records through the normal logging tree.
logger = logging.getLogger("uvicorn.error")


def audit_staff_action(action: str, *, staff_id: int, branch_id: int, success: bool) -> None:
    logger.info(
        "staff_action action=%s staff_id=%s branch_id=%s success=%s",
        action,
        staff_id,
        branch_id,
        success,
    )


def audit_login(*, email: str, success: bool, client: str) -> None:
    logger.info("staff_login email=%s client=%s success=%s", email, client, success)
