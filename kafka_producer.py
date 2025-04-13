from aiokafka import AIOKafkaProducer

producer = None

async def init_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

async def close_kafka_producer():
    global producer
    if producer:
        await producer.stop()

        
