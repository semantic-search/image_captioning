import tensorflow as tf
from config import Config
from model import CaptionGenerator
from dataset import prepare_train_data, prepare_eval_data, prepare_test_data
import csv
import nltk
import time
#import for kafka
from dotenv import load_dotenv
import base64
import os
import uuid
import redis
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
import json
from base64 import decodestring
load_dotenv()
KAFKA_HOSTNAME = os.getenv("KAFKA_HOSTNAME")
KAFKA_PORT = os.getenv("KAFKA_PORT")
REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
# kafka prerequisites
RECEIVE_TOPIC = 'IMAGE_CAP'
SEND_TOPIC_FULL = "IMAGE_RESULTS"
SEND_TOPIC_TEXT = "TEXT"
print("kafka : " + KAFKA_HOSTNAME + ':' + KAFKA_PORT)
# Redis initialize
r = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT,
                      password=REDIS_PASSWORD, ssl=True)
consumer_easyocr = KafkaConsumer(
    RECEIVE_TOPIC,
    bootstrap_servers=[KAFKA_HOSTNAME + ':' + KAFKA_PORT],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="my-group",
    value_deserializer=lambda x: loads(x.decode("utf-8")),
)
# app = FastAPI()
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_HOSTNAME + ':' + KAFKA_PORT],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


nltk.download('punkt')
sess = tf.InteractiveSession()
config = Config()
config.phase = 'test'
config.train_cnn = True
config.beam_size = 3
model = CaptionGenerator(config)
model.load(sess, 'model/289999.npy')
cwd = os.getcwd()

upload_folder = 'test/images/'


def predict(file_name,image_id):
    # f = args['file']
    # f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
    a = time.time()
    data, vocabulary = prepare_test_data(config)
    model.test(sess, data, vocabulary)
    b = time.time()
    print(a - b)
    reader = csv.DictReader(open('test/results.csv'))
    dictobj = next(reader)
    response_dict = {
        "caption": dictobj["caption"],
        "prob": dictobj["prob"],
        "image_id":image_id
    }
    os.remove(upload_folder + file_name)
    os.remove('test/results.csv')
    return response_dict

if __name__ == "__main__":
    print("shit here")
    for message in consumer_easyocr:
        print('xxx--- inside open images consumer---xxx')
        print(KAFKA_HOSTNAME + ':' + KAFKA_PORT)
        message = message.value
        print("MESSAGE RECEIVED consumer_densecap: ")
        image_id = message['image_id']
        # data = message['data']
        data = message['data']
        r.set(RECEIVE_TOPIC, image_id)
        file_name = str(uuid.uuid4()) + ".jpg"

        with open(upload_folder+file_name, "wb") as fh:
            fh.write(base64.b64decode(data.encode("ascii")))

        full_res = predict(file_name,image_id)
        text_res={
            "image_id": full_res["image_id"],
            "captions": full_res["caption"]
        }
        print(full_res)
        producer.send(SEND_TOPIC_FULL, value=json.dumps(full_res))
        producer.send(SEND_TOPIC_TEXT, value=json.dumps(text_res))

        producer.flush()

