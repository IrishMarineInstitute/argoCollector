import json
from pykafka import KafkaClient

class KafkaModule:
  topic = None
  client = None
  def __init__(self,config):
    hosts = config["kafka"]["hosts"]
    topic = config["kafka"]["topic"]
    self.client = KafkaClient(hosts=hosts)
    self.topic = self.client.topics[topic.encode("utf-8")]

  def publish(self,data):
     with self.topic.get_sync_producer() as producer:
        producer.produce(json.dumps(data).encode("utf-8"))

def create_instance(config):
   return KafkaModule(config)
