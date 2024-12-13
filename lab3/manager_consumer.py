import pika
import requests
import json

def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    data = json.loads(body)[0]
    data["description"] = json.dumps(data["description"])
    print(data)

    try:
        response = requests.post("http://localhost:8000/create-product", json=data)
        print(f"Posted to Lab 2: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to POST data: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_from_rabbitmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='iepure_MQ')
    )
    channel = connection.channel()

    channel.queue_declare(queue='data_queue', durable=True)

    channel.basic_consume(queue='data_queue', on_message_callback=callback)

    print("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    consume_from_rabbitmq()
