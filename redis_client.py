import redis.asyncio as redis
from fastapi import APIRouter
from aiokafka import AIOKafkaConsumer
import json
import asyncio

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# async def check_redis():
#     try:
#         pong = await redis_client.ping()
#         print("✅ Redis connected:", pong)
#     except Exception as e:
#         print("❌ Redis connection failed:", e)

# asyncio.run(check_redis())

async def handle_event(event:dict):
    if event["event_type"] == "upload":
        user_id = event["user_id"]
        filename = event["filename"].lower()

        redis_key = f"search_cache:{user_id}:{filename}"
        value = json.dumps([filename])

        await redis_client.set(redis_key,value,ex=300)
    
    if event["event_type"] == "delete":
        user_id = event["user_id"]
        filename = event["filename"].lower()

        redis_key = f"search_cache:{user_id}:{filename}"
        await redis_client.delete(redis_key)


async def consume():
    consumer = AIOKafkaConsumer(
        "file_events",
        bootstrap_servers = "localhost:9092",
        group_id="redis_cache_updater")
    
    await consumer.start()

    try:
        async for msg in consumer:
            event = json.loads(msg.value)
            await handle_event(event)
    
    finally:
        await consumer.stop()
    







