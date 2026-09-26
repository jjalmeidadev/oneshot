"""Topologia RabbitMQ e publicacao duravel dos eventos internos."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from app.alerts.errors import AlertConfigurationError

EXCHANGE="metro.alerts"
DEAD_LETTER_EXCHANGE="metro.alerts.dlx"
DELIVERY_ROUTING_KEY = "notification.delivery.received"
ROUTING_KEYS = (
    "alert.evaluation.requested",
    "alert.notification.requested",
    DELIVERY_ROUTING_KEY,
)


@dataclass(frozen=True)
class Message:
    event_id: str
    event_type: str
    correlation_id: str
    payload: dict[str,Any]


class RabbitMQBroker:
    def __init__(self,url: str|None=None) -> None:
        self.url=url or os.getenv("RABBITMQ_URL","").strip()
        if not self.url: raise AlertConfigurationError("RABBITMQ_URL ausente.")
        self.connection=None; self.channel=None; self.exchange=None

    async def connect(self) -> None:
        try: import aio_pika
        except ImportError as error: raise AlertConfigurationError("Instale aio-pika para usar RabbitMQ.") from error
        self.connection=await aio_pika.connect_robust(self.url)
        self.channel=await self.connection.channel(); await self.channel.set_qos(prefetch_count=10)
        dlx=await self.channel.declare_exchange(DEAD_LETTER_EXCHANGE,aio_pika.ExchangeType.DIRECT,durable=True)
        self.exchange=await self.channel.declare_exchange(EXCHANGE,aio_pika.ExchangeType.TOPIC,durable=True)
        for key in ROUTING_KEYS:
            dlq=await self.channel.declare_queue(f"{key}.dead",durable=True)
            await dlq.bind(dlx,routing_key=key)
            queue=await self.channel.declare_queue(key,durable=True,arguments={"x-dead-letter-exchange":DEAD_LETTER_EXCHANGE,"x-dead-letter-routing-key":key})
            await queue.bind(self.exchange,routing_key=key)

    async def publish(self,message: Message) -> None:
        if self.exchange is None: await self.connect()
        import aio_pika
        body=json.dumps(message.__dict__,ensure_ascii=False,default=str).encode()
        await self.exchange.publish(aio_pika.Message(body=body,message_id=message.event_id,correlation_id=message.correlation_id,delivery_mode=aio_pika.DeliveryMode.PERSISTENT,content_type="application/json"),routing_key=message.event_type)

    async def consume(self,routing_key: str,handler: Callable[[Message],Awaitable[None]]) -> None:
        if self.channel is None: await self.connect()
        queue=await self.channel.get_queue(routing_key)
        async with queue.iterator() as iterator:
            async for incoming in iterator:
                async with incoming.process(requeue=not incoming.redelivered):
                    raw=json.loads(incoming.body); await handler(Message(**raw))

    async def close(self) -> None:
        if self.connection is not None: await self.connection.close()
