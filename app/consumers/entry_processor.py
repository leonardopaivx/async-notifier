import random
import asyncio
from aio_pika import Message
from app.consumers.base_processor import BaseProcessor
from app.memory_store import MemoryStore
from app.config import settings
from app.constants import NotificationStatus


class EntryProcessor(BaseProcessor):
    queue_name = settings.entry_queue

    async def process(self, message: Message):
        trace_id = message.correlation_id

        if random.random() < 0.15:
            MemoryStore.update_status(
                trace_id, NotificationStatus.INITIAL_PROCESSING_FAILURE
            )
            await self.channel.default_exchange.publish(
                Message(body=message.body, correlation_id=trace_id),
                routing_key=settings.retry_queue,
            )
        else:
            await asyncio.sleep(random.uniform(1, 1.5))
            MemoryStore.update_status(
                trace_id, NotificationStatus.INTERMEDIATE_PROCESSED
            )
            await self.channel.default_exchange.publish(
                Message(body=message.body, correlation_id=trace_id),
                routing_key=settings.validation_queue,
            )


if __name__ == "__main__":
    import asyncio

    asyncio.run(EntryProcessor().run())
