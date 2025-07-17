import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from aio_pika.abc import AbstractChannel

from app.rabbit import Rabbit
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Rabbit.connect()
    yield
    await Rabbit.close()


app = FastAPI(lifespan=lifespan)


async def get_channel() -> AbstractChannel:
    return await Rabbit.get_channel()


@app.get("/health")
async def health_check():
    try:
        channel = await Rabbit.get_channel()
        await channel.declare_queue(settings.entry_queue, passive=True)
        return {"status": "ok"}
    except Exception as e:
        logger.error("Health check failed", exc_info=e)
        raise HTTPException(status_code=503, detail="RabbitMQ unavailable")
