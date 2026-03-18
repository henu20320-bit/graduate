from sqlalchemy.orm import Session

from app.models import SystemLog


class SystemLogService:
    @staticmethod
    def write_log(db: Session, module: str, action: str, status: str, message: str) -> SystemLog:
        log = SystemLog(module=module, action=action, status=status, message=message)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
