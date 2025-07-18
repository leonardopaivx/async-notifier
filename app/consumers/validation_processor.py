import random
import asyncio
from aio_pika import Message
from app.consumers.base_processor import BaseProcessor
from app.memory_store import MemoryStore
from app.config import settings
from app.constants import NotificationStatus


class ValidationProcessor(BaseProcessor):
    queue_name = settings.validation_queue

    async def process(self, message: Message):
        trace_id = message.correlation_id
        await asyncio.sleep(random.uniform(0.5, 1))
        if random.random() < 0.05:
            MemoryStore.update_status(trace_id, NotificationStatus.FINAL_SEND_FAILURE)
            await self.channel.default_exchange.publish(
                Message(body=message.body, correlation_id=trace_id),
                routing_key=settings.dlq_queue,
            )
        else:
            MemoryStore.update_status(trace_id, NotificationStatus.SENT_SUCCESS)


if __name__ == "__main__":
    import asyncio

    asyncio.run(ValidationProcessor().run())
