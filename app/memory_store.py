from datetime import datetime, timezone
from typing import Dict, Any
from app.constants import NotificationStatus


class MemoryStore:
    _store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create(cls, trace_id: str, data: Dict[str, Any]) -> None:
        cls._store[trace_id] = {
            **data,
            "status": NotificationStatus.RECEIVED,
            "history": [
                {
                    "status": NotificationStatus.RECEIVED,
                    "timestamp": datetime.now(timezone.utc),
                }
            ],
        }

    @classmethod
    def update_status(cls, trace_id: str, status: NotificationStatus) -> None:
        record = cls._store.get(trace_id)
        if record:
            record["status"] = status
            record["history"].append(
                {"status": status, "timestamp": datetime.now(timezone.utc)}
            )

    @classmethod
    def get(cls, trace_id: str) -> Dict[str, Any]:
        return cls._store.get(trace_id)
