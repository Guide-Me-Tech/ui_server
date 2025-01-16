from kafka import KafkaProducer, KafkaConsumer
import uuid


class TestKafka:
    def setup_method(self):
        self.topic_name = str(uuid.uuid4())
        print("TOPIC NAME: ", self.topic_name)

    def test_producer(self):
        producer = KafkaProducer(
            bootstrap_servers=[
                "34.34.91.15.154:19092",
                "34.34.91.15.154:29092",
                "34.34.91.15.154:39092",
            ]
        )
        topic = self.topic_name

        for i in range(100):
            message = f"Test message_{i}"
            message = message.encode("utf-8")
            # Send a message
            future = producer.send(topic, message)
            result = future.get(timeout=10)

        # Check if the message was sent successfully
        assert result is not None
        producer.close()

    def test_consumer(self):
        consumer = KafkaConsumer(
            "test_topic",
            bootstrap_servers=[
                "34.34.91.15.154:19092",
                "34.34.91.15.154:29092",
                "34.34.91.15.154:39092",
            ],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="test_group",
        )

        # Poll for new messages
        consumer.poll(timeout_ms=1000)

        # Check if we can consume a message
        messages = []
        for message in consumer:
            print(message)
            messages.append(message.value)
        assert len(messages) == 100
        consumer.close()


if __name__ == "__main__":
    tf = TestKafka()
    tf.setup_method()
    tf.test_producer()
    tf.test_consumer()
