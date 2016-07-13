import json
from pykafka import KafkaClient
from pykafka.common import OffsetType

class KafkaModule:
  topic = None
  client = None
  consumer_group = None
  def __init__(self,config):
    hosts = config["kafka"]["hosts"]
    topic = config["kafka"]["topic"]
    self.client = KafkaClient(hosts=hosts)
    self.topic = self.client.topics[topic.encode("utf-8")]
    self.consumer_group = config["kafka"]["consumer_group"].encode("utf-8")

  def publish(self,data):
     with self.topic.get_sync_producer() as producer:
        producer.produce(json.dumps(data).encode("utf-8"))

  def produce(self,data):
     consumer = self.topic.get_simple_consumer(
        consumer_group=self.consumer_group,
        auto_offset_reset=OffsetType.EARLIEST,
        reset_offset_on_start=False
     )
     for message in consumer:
        if message is not None:
            result = json.loads(message.value.decode("utf-8"))
            yield (data,result)

def create_instance(config):
   return KafkaModule(config)
