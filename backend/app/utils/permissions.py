from datetime import datetime, timedelta, timezone


def can_modify_record(created_at: datetime, role: str, is_owner: bool) -> bool:
    """Check if user can modify a record.

    Admin: always can.
    Employee owner: can only within 30 days.
    Others: cannot.
    """
    if role == "admin":
        return True
    if role == "employee" and is_owner:
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        return created_at >= cutoff
    return False


def can_delete_record(created_at: datetime, role: str, is_owner: bool) -> bool:
    """Same logic as can_modify_record."""
    return can_modify_record(created_at, role, is_owner)
