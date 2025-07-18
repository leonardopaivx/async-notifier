import random
import asyncio
from aio_pika import Message
from app.consumers.base_processor import BaseProcessor
from app.memory_store import MemoryStore
from app.config import settings
from app.constants import NotificationStatus


class RetryProcessor(BaseProcessor):
    queue_name = settings.retry_queue

    async def process(self, message: Message):
        trace_id = message.correlation_id
        await asyncio.sleep(3)
        if random.random() < 0.2:
            MemoryStore.update_status(
                trace_id, NotificationStatus.FINAL_REPROCESS_FAILURE
            )
            await self.channel.default_exchange.publish(
                Message(body=message.body, correlation_id=trace_id),
                routing_key=settings.dlq_queue,
            )
        else:
            MemoryStore.update_status(trace_id, NotificationStatus.REPROCESSING_SUCCESS)
            await self.channel.default_exchange.publish(
                Message(body=message.body, correlation_id=trace_id),
                routing_key=settings.validation_queue,
            )


if __name__ == "__main__":
    import asyncio

    asyncio.run(RetryProcessor().run())
