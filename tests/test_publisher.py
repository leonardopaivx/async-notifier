import pytest
from unittest.mock import AsyncMock
from aio_pika.abc import AbstractChannel

from app.schemas import NotificationRequest
from app.main import _publish_notification


@pytest.mark.asyncio
async def test_publish_notification(monkeypatch):
    fake_channel = AsyncMock(spec=AbstractChannel)
    fake_exchange = AsyncMock()
    fake_channel.default_exchange = fake_exchange

    payload = NotificationRequest(message_content="Teste", notification_type="EMAIL")

    result = await _publish_notification(payload, fake_channel)

    assert "message_id" in result
    assert "trace_id" in result
    assert result["message_id"] == payload.message_id

    fake_exchange.publish.assert_awaited_once()
