import json
import pika

class CloudAMQPClient:
    def __init__(self, cloud_amqp_url, queue_name):
        self.cloud_amqp_url = cloud_amqp_url
        self.queue_name = queue_name
        self.params = pika.URLParameters(cloud_amqp_url)
        self.params.socket_timeout = 10
        self.connection = pika.BlockingConnection(self.params) # Connect to CloudAMQP
        self.channel = self.connection.channel() # start a channel
        self.channel.queue_declare(queue=queue_name) # Declare a queue

    def sendMessage(self, message):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
        print '[x] Sent message to %s' % self.queue_name

    def getMessage(self):
        method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
        if method_frame:
            print '[x] Received message from %s' % self.queue_name
            self.channel.basic_ack(method_frame.delivery_tag)
            return json.loads(body)
        else:
            return None

    # BlockingConnection.sleep is a safer way to sleep than time.sleep(). This
    # will repond to server's heartbeat.
    def sleep(self, seconds):
        self.connection.sleep(seconds)