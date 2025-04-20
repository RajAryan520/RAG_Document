from aiokafka import AIOKafkaProducer
import asyncio
producer = None

async def init_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

async def close_kafka_producer():
    global producer
    if producer:
        await producer.stop()


# async def check_kafka():
#     try:
#         producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
#         await producer.start()
#         print("✅ Kafka is reachable")
#         await producer.stop()
#     except Exception as e:
#         print("❌ Kafka connection failed:", e)

# asyncio.run(check_kafka())