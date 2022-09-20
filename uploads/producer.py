from sqlite3 import Timestamp
from confluent_kafka import Producer
import json
import time
from datetime import timedelta, datetime
import logging
import random
from sys import argv   

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='producer.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_producer(broker="localhost:9092"):
    p=Producer({'bootstrap.servers': broker})
    print('Kafka Producer has been initiated...')
    


def receipt(err,msg):
    
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = '{}: {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)


def main(broker="localhost:29092", topic="kafkaTopic", speaker_list=["Speaker1", "Speaker2", "Speaker3"], file="words.txt"):
    
    p=Producer({'bootstrap.servers': broker})
    print('Kafka Producer has been initiated...')

    speakers = dict()
    for speaker in speaker_list:
        speakers[speaker] = datetime.now()
    
    word_list = []
    with open(file, "r") as words:
        for line in words.readlines():
            word_list.append(line.strip())
    for word in word_list:
        speaker = random.choice(list(speakers.keys()))
        data={
           'speaker': speaker,
           'time': str(speakers.get(speaker)),
           'word': word 
           }

        speakers[speaker] += timedelta(seconds=0.5)

        m=json.dumps(data)
        p.poll(1)
        p.produce(topic, m.encode('utf-8'), callback=receipt)
        time.sleep(5)
        p.flush()


if __name__=="__main__":


    if len(argv) > 1:
        broker = argv[1]
        topic = argv[2]
        speaker_list = argv[3].split()
        file = argv[4]       
        main(broker, topic, speaker_list, file)
    else:
        main()