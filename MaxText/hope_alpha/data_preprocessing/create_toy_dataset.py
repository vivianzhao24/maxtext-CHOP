import tensorflow as tf
import pandas as pd 
from transformers import AutoTokenizer
import os
import numpy as np

def create_example(text):
    # Create a dictionary mapping the feature name to the tf.train.Feature
    feature = {
        'text': tf.train.Feature(bytes_list=tf.train.BytesList(value=[text.encode()]))
    }
    
    # Create a Features message using tf.train.Example
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def write_tfrecords(data, filename):
    with tf.io.TFRecordWriter(filename) as writer:
        for text in data:
            example = create_example(text)
            writer.write(example)

def create_toy_tfrecords(): 
    data = ["This is toy example number " + str(n) for n in range(1,101)]
    # Specify the TFRecord filename
    filename = 'toy_dataset.tfrecord'

    # Write the dataset to a TFRecord file
    write_tfrecords(data, filename)

"""
from maxtext/MaxText/sequence_packing.py
Two input examples get combined to form an output example.
  The input examples are:
  {"inputs": [8, 7, 1, 0], "targets":[4, 1, 0]}
  {"inputs": [2, 3, 4, 1], "targets":[5, 6, 1]}
The output example is:
  {
                 "inputs": [8, 7, 1, 2, 3, 4, 1, 0, 0, 0]
    "inputs_segmentation": [1, 1, 1, 2, 2, 2, 2, 0, 0, 0]
        "inputs_position": [0, 1, 2, 0, 1, 2, 3, 0, 0, 0]
                "targets": [4, 1, 5, 6, 1, 0, 0, 0, 0, 0]
   "targets_segmentation": [1, 1, 2, 2, 2, 0, 0, 0, 0, 0]
       "targets_position": [0, 1, 0, 1, 2, 0, 0, 0, 0, 0]
  }
"""

def create_toy_jsonl(num_files, samples_per, region): 
    auth_token = os.getenv("HF_AUTH_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B", use_auth_token=auth_token)
    # Each list of input_ids will be 12 integers long
    text = ['This is the first segment. This is the second segment'] * samples_per
    segment_ids = [0] * 7 + [1] * 5
    segment_ids = [segment_ids] * samples_per 
    inputs_position = [np.concatenate([np.arange(7), np.arange(5)])] * samples_per  
    encodings = tokenizer(text)
    index = 0
    for i in range(num_files): 
        #df = pd.DataFrame({'input_ids': encodings['input_ids'], 'segment_ids': segment_ids}) 
        # used numpy to cast as int32, but this is not necessary. 
        df = pd.DataFrame({
        'input_ids': [np.array(ids, dtype=np.int32) for ids in encodings['input_ids']],
        'inputs_segmentation': [np.array(ids, dtype=np.int32) for ids in segment_ids],
        'inputs_position': inputs_position,
        'targets_segmentation': [np.array(ids, dtype=np.int32) for ids in segment_ids],
        'targets_position': inputs_position
        })
        df['sample_id'] = df.index.values + samples_per * i
        df.to_json(f'gs://scit1565-pedsllm-b5-{region.lower()}1/datasets/toy_dataset/raw/toy_segments_{i}.jsonl', orient='records', lines=True, index=False)

def create_toy_iterator_test_jsonl(num_files, samples_per, region): 
    "create a dataset used for testing the checkpointing of the iterator"
    
    for i in range(num_files): 
        #df = pd.DataFrame({'input_ids': encodings['input_ids'], 'segment_ids': segment_ids}) 
        # used numpy to cast as int32, but this is not necessary. 
        id_range = np.arange(samples_per) + i * samples_per
        df = pd.DataFrame({
        'input_ids': [np.full(12, i_d, dtype=np.int32) for i_d in id_range],
        'inputs_segmentation': [np.full(12, 1, dtype=np.int32) for i_d in id_range],
        'inputs_position': [np.arange(12, dtype=np.int32) for i_d in id_range],
        'targets_segmentation': [np.full(12, 1, dtype=np.int32) for i_d in id_range],
        'targets_position': [np.arange(12, dtype=np.int32) for i_d in id_range],
        })
        df['sample_id'] = df.index.values + samples_per * i
        print(df.head())
        #df.to_json(f'gs://scit1565-pedsllm-b5-{region.lower()}1/datasets/toy_dataset_iterator_test/raw/toy_segments_{i}.jsonl', orient='records', lines=True, index=False)

if __name__ == "__main__": 
    create_toy_jsonl(5, 100, 'south')
    #create_toy_iterator_test_jsonl(5, 100, "south")
