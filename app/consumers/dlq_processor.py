import logging
from aio_pika.abc import AbstractMessage
from app.consumers.base_processor import BaseProcessor
from app.config import settings

logger = logging.getLogger(__name__)


class DlqProcessor(BaseProcessor):
    queue_name = settings.dlq_queue

    async def process(self, message: AbstractMessage):
        logger.error(
            f"DLQ message: {message.correlation_id} -> {message.body.decode()}"
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(DlqProcessor().run())
