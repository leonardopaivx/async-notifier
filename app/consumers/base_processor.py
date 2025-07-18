# app/consumers/base_processor.py
import abc
import logging
from aio_pika import connect_robust
from aio_pika.abc import AbstractMessage, AbstractChannel
from app.config import settings

logger = logging.getLogger(__name__)


class BaseProcessor(abc.ABC):
    queue_name: str
    channel: AbstractChannel

    async def run(self):
        connection = await connect_robust(settings.rabbit_url)
        self.channel = await connection.channel()

        queue = await self.channel.declare_queue(
            self.queue_name, durable=True, arguments={"x-dead-letter-exchange": "dlx"}
        )

        logger.info(f"Starting consumer for {self.queue_name}")

        async with queue.iterator() as messages:
            async for message in messages:
                async with message.process():
                    try:
                        await self.process(message)
                    except Exception:
                        logger.exception(
                            f"Error processing message {message.correlation_id}"
                        )

    @abc.abstractmethod
    async def process(self, message: AbstractMessage): ...
