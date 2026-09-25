from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.audit import AuditLog


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "action": log.action,
            "entity": log.entity,
            "user": log.user,
            "timestamp": log.timestamp,
            "diff": log.diff,
        }
        for log in logs
    ]