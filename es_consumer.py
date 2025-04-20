from elasticsearch import AsyncElasticsearch
from aiokafka import AIOKafkaConsumer
import json
import asyncio
es = AsyncElasticsearch("http://localhost:9200")

# async def check_es_connection():
#     try:
#         if await es.ping():
#             print("Connected to Elasticsearch")
#             await es.close()
#     except Exception as e:
#             print("Failed to connect to Elasticsearch",e)

# asyncio.run(check_es_connection())

async def handle_event(event: dict):
    if event["event_type"] == "upload":
        await es.index(
            index="documents",
            id=event["doc_id"],
            document={
                "user_id": event["user_id"],
                "filename": event["filename"],
                "timestamp": event["timestamp"]
            }
        )

    elif event["event_type"] == "delete":
        await es.delete(
            index="documents",
            id=event["doc_id"]
        )

async def consume():
    consumer = AIOKafkaConsumer(
        "file_events",
        bootstrap_servers="localhost:9092",
        group_id="es_index_updater"
    )
    await consumer.start()

    try:
        async for msg in consumer:
            event = json.loads(msg.value)
            await handle_event(event)
    finally:
        await consumer.stop()