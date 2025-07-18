import json
import os
from threading import Lock
from datetime import datetime, timezone
from typing import Dict, Any
from app.constants import NotificationStatus


class MemoryStore:
    _file_path = os.getenv("MEMORY_STORE_PATH", "/app/state/store.json")
    _lock = Lock()

    @classmethod
    def _load_store(cls) -> Dict[str, Any]:
        if not os.path.exists(cls._file_path):
            return {}
        try:
            with open(cls._file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    @classmethod
    def _save_store(cls, store: Dict[str, Any]) -> None:
        dirpath = os.path.dirname(cls._file_path)
        os.makedirs(dirpath, exist_ok=True)

        tmp = cls._file_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(store, f, default=str, indent=2)
        os.replace(tmp, cls._file_path)

    @classmethod
    def create(cls, trace_id: str, data: Dict[str, Any]) -> None:
        with cls._lock:
            store = cls._load_store()
            store[trace_id] = {
                "message_id": data["message_id"],
                "message_content": data["message_content"],
                "notification_type": data["notification_type"],
                "status": NotificationStatus.RECEIVED.name,
                "history": [
                    {
                        "status": NotificationStatus.RECEIVED.name,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }
            cls._save_store(store)

    @classmethod
    def update_status(cls, trace_id: str, status: NotificationStatus) -> None:
        with cls._lock:
            store = cls._load_store()
            record = store.get(trace_id)
            if not record:
                return
            record["status"] = status.name
            record.setdefault("history", []).append(
                {
                    "status": status.name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            cls._save_store(store)

    @classmethod
    def get(cls, trace_id: str) -> Dict[str, Any]:
        with cls._lock:
            return cls._load_store().get(trace_id)
