import logging
from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel
from app.config import settings

logger = logging.getLogger(__name__)


class Rabbit:
    _connection = None
    _channel: AbstractChannel = None

    @classmethod
    async def connect(cls) -> AbstractChannel:
        if cls._connection is None:
            cls._connection = await connect_robust(settings.rabbit_url)
            cls._channel = await cls._connection.channel()
            logger.info("Connected to RabbitMQ")
        return cls._channel

    @classmethod
    async def get_channel(cls) -> AbstractChannel:
        if cls._channel is None:
            raise RuntimeError("RabbitMQ connection not established")
        return cls._channel

    @classmethod
    async def close(cls) -> None:
        if cls._connection:
            await cls._connection.close()
            logger.info("RabbitMQ connection closed")
            cls._connection = None
            cls._channel = None
