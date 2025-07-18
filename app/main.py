import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from uuid import uuid4
from aio_pika import Message, ExchangeType
from aio_pika.abc import AbstractChannel

from app.rabbit import Rabbit
from app.memory_store import MemoryStore
from app.schemas import NotificationRequest, StatusResponse
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    channel = await Rabbit.connect()

    dlx = await channel.declare_exchange("dlx", ExchangeType.DIRECT, durable=True)

    for queue_name in (
        settings.entry_queue,
        settings.retry_queue,
        settings.validation_queue,
    ):
        await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": "dlx"},
        )

    dlq = await channel.declare_queue(
        settings.dlq_queue,
        durable=True,
        arguments={"x-dead-letter-exchange": "dlx"},
    )

    for queue_name in (
        settings.entry_queue,
        settings.retry_queue,
        settings.validation_queue,
    ):
        await dlq.bind(dlx, routing_key=queue_name)

    yield
    await Rabbit.close()


app = FastAPI(lifespan=lifespan)


async def get_channel() -> AbstractChannel:
    return await Rabbit.get_channel()


async def _publish_notification(
    payload: NotificationRequest,
    channel: AbstractChannel,
) -> dict:
    """
    Core logic to publish a notification message.
    """
    trace_id = str(uuid4())
    MemoryStore.create(trace_id, payload.model_dump())
    await channel.default_exchange.publish(
        Message(
            body=payload.model_dump_json().encode(),
            content_type="application/json",
            correlation_id=trace_id,
        ),
        routing_key=settings.entry_queue,
    )
    return {"message_id": payload.message_id, "trace_id": trace_id}


@app.post("/api/notify", status_code=202)
async def send_notification(
    payload: NotificationRequest,
    channel: AbstractChannel = Depends(get_channel),
):
    return await _publish_notification(payload, channel)


@app.get("/api/notification/status/{trace_id}", response_model=StatusResponse)
async def get_status(trace_id: str):
    record = MemoryStore.get(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Trace ID not found")
    return StatusResponse(
        trace_id=trace_id,
        message_id=record["message_id"],
        message_content=record["message_content"],
        notification_type=record["notification_type"],
        status=record["status"],
        history=record["history"],
    )


@app.get("/health")
async def health_check(
    channel: AbstractChannel = Depends(get_channel),
):
    await channel.declare_queue(settings.entry_queue, passive=True)
    return {"status": "ok"}
