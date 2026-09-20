"""
Circuit breaker (pybreaker) and Kafka event publishing helpers.
Equivalent to Resilience4j's @CircuitBreaker and Spring Kafka's KafkaTemplate.
"""
import json
import logging
import os

import pybreaker
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# One shared breaker per outbound dependency type is typical; services can
# import `build_breaker` to make a named breaker per downstream call.
def build_breaker(name: str, fail_max: int = 5, reset_timeout: int = 30) -> pybreaker.CircuitBreaker:
    return pybreaker.CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        name=name,
    )


class EventPublisher:
    """Lazily-connected Kafka producer with graceful degradation."""

    def __init__(self):
        self._producer = None

    def _get_producer(self):
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: str(k).encode("utf-8") if k is not None else None,
                request_timeout_ms=5000,
            )
        return self._producer

    def publish(self, topic: str, key, event: dict):
        try:
            producer = self._get_producer()
            producer.send(topic, key=key, value=event)
            producer.flush(timeout=5)
        except KafkaError as exc:
            # Publishing failures should never break the primary request flow.
            logger.warning("Kafka publish failed for topic=%s: %s", topic, exc)


event_publisher = EventPublisher()
