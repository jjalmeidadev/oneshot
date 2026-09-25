"""Smoke test AMQP isolado, sem escrever nas filas funcionais."""

from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from dotenv import load_dotenv

from app.alerts.messaging import Message, RabbitMQBroker


async def run() -> None:
    load_dotenv()
    broker = RabbitMQBroker()
    await broker.connect()
    assert broker.channel is not None
    assert broker.exchange is not None
    routing_key = f"smoke.{uuid4()}"
    queue = await broker.channel.declare_queue(exclusive=True, auto_delete=True)
    await queue.bind(broker.exchange, routing_key=routing_key)
    expected = Message(
        event_id=str(uuid4()),
        event_type=routing_key,
        correlation_id="rabbitmq-smoke",
        payload={"probe": True},
    )
    await broker.publish(expected)
    incoming = await queue.get(timeout=5, fail=False)
    if incoming is None:
        raise RuntimeError("RabbitMQ nao entregou a mensagem de smoke test.")
    received = json.loads(incoming.body)
    await incoming.ack()
    if received.get("event_id") != expected.event_id:
        raise RuntimeError("RabbitMQ devolveu uma mensagem inesperada.")
    await queue.delete()
    await broker.close()
    print("RABBITMQ_SMOKE=ok")


if __name__ == "__main__":
    asyncio.run(run())
