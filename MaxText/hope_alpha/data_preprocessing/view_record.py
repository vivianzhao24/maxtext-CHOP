#!/usr/bin/env -S conda run --no-capture-output -n convert-checkpoint python

import json
import tensorflow as tf
from google.cloud import storage
import numpy as np
import os
from google.protobuf.json_format import MessageToDict

def view_record(): 
  
    ds = tf.data.TFRecordDataset('gs://scit1565-pedsllm-b5-south1/datasets/identified_notes/packed/tfrecord-data/2018-01.tfrecords')
    for record in ds.take(1): 
        example = tf.train.Example()
        example.ParseFromString(record.numpy())
        example_dict = MessageToDict(example)
        print(example_dict['features']['feature']['targets_position'])

def view_json(): 
    client = storage.Client()
    bucket = client.get_bucket('scit1565-pedsllm-b5-east5')
    #file_path = 'datasets/notes/1.0/dataset_info.json'
    file_path = 'datasets/notes/1.0/features.json'
    blob = bucket.blob(file_path)

    json_data = blob.download_as_text()

    json_content = json.loads(json_data)
    print(json.dumps(json_content, indent=4))


    
if __name__ == "__main__":
    #view_record()
    view_json()
