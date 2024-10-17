#!/usr/bin/env -S conda run --no-capture-output -n convert-checkpoint python
"""
Example usage with arcus tasks 
With window of one year: 
    lab-tasks submit-script --name maxtext-tfrecords-2000-2009 --path \
    /home/donatim/maxtext/MaxText/hope_alpha/convert_jsonl_to_tfrecord.py --cpu 5 --memory 50  --split 10 --parallel 10

https://cloud.google.com/storage/docs/deleting-objects#storage-delete-object-python
https://cloud.google.com/storage/docs/streaming-uploads
output_blob = input_bucket.blob(gcs_tfrecord_file.replace("gs://"+input_bucket_name+"/",""))
        print('output blob', output_blob)

        if not output_blob.exists():
"""
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from google.cloud import storage
import numpy as np

import math
import tempfile 
import tensorflow_datasets as tfds
import itertools


def jsonl_to_tfrecord(gcs_jsonl_path, gcs_tfrecord_file):
    client = storage.Client()
    input_bucket_name, input_file_path = gcs_jsonl_path.replace('gs://', '').split('/', 1)
    input_bucket = client.get_bucket(input_bucket_name)
    input_blob = input_bucket.blob(input_file_path)
    

    with tf.io.TFRecordWriter(gcs_tfrecord_file) as writer:
        for line in input_blob.download_as_string().decode('utf-8').splitlines():
            try:
                data = json.loads(line)
                # Create features dictionary (adjust based on your data)
                features = {
                                'text': tf.train.Feature(bytes_list=tf.train.BytesList(value=[data['text'].encode('utf-8')]))
                                
                            }

                # Create an Example protocol buffer
                example = tf.train.Example(features=tf.train.Features(feature=features))

                # Write the serialized example to the TFRecord file
                writer.write(example.SerializeToString())
                print("Success")

            except:
                print(f"Error in parsing {line}")

def jsonl_to_tfrecord_one_file(gcs_jsonl_path, gcs_tfrecord_file, token_ids_col='inputs'):

    client = storage.Client()
    input_bucket_name, input_file_path = gcs_jsonl_path.replace('gs://', '').split('/', 1)
    input_bucket = client.get_bucket(input_bucket_name)
    input_blob = input_bucket.blob(input_file_path)
    
    
    with tf.io.TFRecordWriter(gcs_tfrecord_file) as writer:
        for line in input_blob.download_as_string().decode('utf-8').splitlines():
            try:
                data = json.loads(line)
                # data['input_ids'] is a list
                # Create features dictionary (adjust based on your data)
                
                features = {
                                # Uncomment this line for string column(s)
                                #'text': tf.train.Feature(bytes_list=tf.train.BytesList(value=[data['text'].encode('utf-8')])),
                                'inputs': tf.train.Feature(int64_list=tf.train.Int64List(value=data[token_ids_col])), 
                                'inputs_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_segmentation'])), 
                                'inputs_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_position'])), 
                                'targets_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_segmentation'])), 
                                'targets_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_position']))
                            }

                # Create an Example protocol buffer
                example = tf.train.Example(features=tf.train.Features(feature=features))

                # Write the serialized example to the TFRecord file
                writer.write(example.SerializeToString())

            except Exception:
                print(f"Error in parsing {line}")
                raise
    # else:
    #     print(f"Skipping {output_blob} because it already exists")


def parse_example(line, token_ids_col): 
    data = json.loads(line)
    # data['input_ids'] is a list
    # Create features dictionary (adjust based on your data)
    
    features = {
        # Uncomment this line for string column(s)
        #'text': tf.train.Feature(bytes_list=tf.train.BytesList(value=[data['text'].encode('utf-8')])),
        'inputs': tf.train.Feature(int64_list=tf.train.Int64List(value=data[token_ids_col])), 
        'inputs_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_segmentation'])), 
        'inputs_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_position'])), 
        'targets_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_segmentation'])), 
        'targets_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_position']))
    }

    # Create an Example protocol buffer
    example = tf.train.Example(features=tf.train.Features(feature=features))
    return example 

def jsonl_to_tfrecord_one_file_split(gcs_jsonl_path, gcs_tfrecord_file, temp_dir, per_split=256, token_ids_col='inputs'):

    client = storage.Client()
    bucket_name, input_file_path = gcs_jsonl_path.replace('gs://', '').split('/', 1)
    base_output_file_path =   gcs_tfrecord_file.replace('gs://', '').split('/', 1)[1]
    bucket = client.get_bucket(bucket_name)
    input_blob = bucket.blob(input_file_path)
    lines = input_blob.download_as_string().decode('utf-8').splitlines()
    num_splits = math.ceil(len(lines) / per_split)
    
    for split in range(num_splits):
        output_file_path = base_output_file_path.replace('.tfrecords',"_{:03d}-of-{:03d}.tfrecords".format(split + 1, num_splits))
        temp_file_prefix = output_file_path.split('/')[-1].split('.')[0]
        with tempfile.NamedTemporaryFile(prefix=temp_file_prefix, suffix=".tfrecords", dir=temp_dir, delete=True) as temp_file:
            temp_file_path = temp_file.name
            with tf.io.TFRecordWriter(temp_file_path) as writer:
                for line in lines[split * per_split: min((split + 1) * per_split, len(lines))]:
            
                    try:
                        example = parse_example(line, token_ids_col)

                        # Write the serialized example to the TFRecord file
                        writer.write(example.SerializeToString())

                    except Exception:
                        print(f"Error in parsing {line}")
                        raise
        
            output_blob = bucket.blob(output_file_path)
            #generation_match_precondition = 0
            # Should be synchronous by default. 
            output_blob.upload_from_filename(temp_file_path)

def rename_records_combined():
    """This function was used to prepare notes_replay_combined, a dataset with notes and replay"""

    prefixes = ['datasets/finetune/interleaved/tfrecords/', 'datasets/replay/interleaved/tfrecords/', 'datasets/identified_notes/interleaved/tfrecords/']
    client = storage.Client()
    # Get the source and target buckets
    bucket = client.bucket('scit1565-pedsllm-b5-east5')
    all_blobs = itertools.chain.from_iterable(
        [bucket.list_blobs(prefix=prefix) for prefix in prefixes]
    )
    all_blobs = list(all_blobs)
    count = len(all_blobs)
    ix = 0
    # Iterate through each file to rename
    for blob in all_blobs:
        # Believe that format when using {SHARD_X_OF_Y} naming convention expects the zerio-indexed index of the file in place of X and the number of files in place of Y, 
        # so if you had two files the second file would be named 00001-of-00002 instead of 00002-of-00002
        # See https://www.tensorflow.org/datasets/external_tfrecord
        filename = "datasets/notes_replay_combined/1.0/notes_replay_combined-train.tfrecord-{:05d}-of-{:05d}".format(ix, count)
        bucket.copy_blob(blob, bucket, filename)
        ix += 1 



def rename_records():
    """This function was used to prepare datasets/notes/1.0, a notes only dataset"""
    #"gs://scit1565-pedsllm-b5-east5/datasets/identified_notes/interleaved/tfrecords/"

    client = storage.Client()
    # Get the source and target buckets
    bucket = client.bucket('scit1565-pedsllm-b5-east5')
   
    # List all blobs (files) in the source bucket
    blobs = bucket.list_blobs(prefix='datasets/identified_notes/interleaved/tfrecords/')
    count = 0 
    for b in blobs: 
        count += 1
    ix = 0
    print('count', count)
    # Iterate through each file in the source bucket
    blobs = bucket.list_blobs(prefix='datasets/identified_notes/interleaved/tfrecords/')
    for blob in blobs:
        filename = "datasets/notes/1.0/notes-train.tfrecord-{:05d}-of-{:05d}".format(ix, count)
       
    
        bucket.copy_blob(blob, bucket, filename)

        ix += 1 
        
def jsonl_to_tfrecord_all_files(gcs_jsonl_path, prefix, gcs_tfrecord_path, token_ids_col='inputs'):
    client = storage.Client()
    input_bucket_name = gcs_jsonl_path.replace('gs://', '')
    input_bucket = client.get_bucket(input_bucket_name)

    input_blobs = input_bucket.list_blobs(prefix=prefix)
    
    for input_blob in input_blobs:
    
        gcs_tfrecord_file = gcs_tfrecord_path+input_blob.name.split('/')[-1].replace('jsonl','tfrecords')
        output_blob = input_bucket.blob(gcs_tfrecord_file.replace("gs://"+input_bucket_name+"/",""))

        # change if you don't want to be able to overwrite existing records: 
        #if not output_blob.exists():
        
        with tf.io.TFRecordWriter(gcs_tfrecord_file) as writer:
            for line in input_blob.download_as_string().decode('utf-8').splitlines():
                try:
                    data = json.loads(line)
                    # data['input_ids'] is a list
                    # Create features dictionary (adjust based on your data)
                    
                    features = {
                                    # Uncomment this line for string column(s)
                                    #'text': tf.train.Feature(bytes_list=tf.train.BytesList(value=[data['text'].encode('utf-8')])),
                                    'inputs': tf.train.Feature(int64_list=tf.train.Int64List(value=data[token_ids_col])), 
                                    'inputs_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_segmentation'])), 
                                    'inputs_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['inputs_position'])), 
                                    'targets_segmentation': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_segmentation'])), 
                                    'targets_position': tf.train.Feature(int64_list=tf.train.Int64List(value=data['targets_position'])) 
                                 
                                }

                    # Create an Example protocol buffer
                    example = tf.train.Example(features=tf.train.Features(feature=features))

                    # Write the serialized example to the TFRecord file
                    writer.write(example.SerializeToString())

                except Exception:
                    print(f"Error in parsing {line}")
                    raise
        # else:
        #     print(f"Skipping {output_blob} because it already exists")


def convert_toy_dataset():
    # Usage (assuming GCS URI format)
    # Location of jsonl - gs://scit1565-pedsllm-b5-south1/datasets/toy_dataset/raw/toy_segments.jsonl'
    gcs_jsonl_bucket = 'gs://scit1565-pedsllm-b5-south1' # Note the lack of trailing forward slash 
    #prefix = 'datasets/toy_dataset_iterator_test/raw/toy_segments'
    prefix = 'datasets/toy_dataset/raw/toy_segments'
    tfrecord_path = gcs_jsonl_bucket+'/datasets/toy_dataset/tfrecord-data/' 
    #tfrecord_path = gcs_jsonl_bucket+'/datasets/toy_dataset_iterator_test/tfrecord-data/' 
    jsonl_to_tfrecord_all_files(gcs_jsonl_bucket, prefix, tfrecord_path, token_ids_col='input_ids') 


def date_lists():
    "Return window of n years (or less on edge case), that slides with split number (for use with arcus tasks), and all 12 months"
    starting_year = 2010
    ending_year = 2019
    window = 1
    year_range = list(range(starting_year, ending_year + 1))
    years = [str(y) for y in year_range]
    split = int(os.getenv('SPLIT_ID'))
    s_ix = split - 1 # splits are not zero-indexed 
    years = years[s_ix * window: min((s_ix + 1) * window, len(years))] 
    months = ["{:02d}".format(m) for m in range(1, 13)]    
    return years, months 

def date_lists_split_years(split):
    "Return window of n years (or less on edge case), that slides with split number (for use with arcus tasks), and all 12 months"
    starting_year = 2020
    ending_year = 2023
    window = 3
    split_num = 8 
    task_ix = 1
   
    split_ix = split - 1 # splits are not zero-indexed 

    year_range = list(range(starting_year, ending_year + 1))
    years = [str(y) for y in year_range]
    months = ["{:02d}".format(m) for m in range(1, 13)]  
    date_tups = [(y, m) for y in years for m in months ]
    
    start_ix =  split_ix * window   
    end_ix = (split_ix + 1) * window
    start_ix = start_ix + (window * split_num * task_ix)
    end_ix = end_ix + (window * split_num * task_ix)

    date_tups_partial = date_tups[start_ix: min(end_ix, len(date_tups))] 
    
    return date_tups_partial

def convert_all_notes(): 
    gcs_base_path = "gs://scit1565-pedsllm-b5-east5" # note no trailing fwd slash   
  
    years, months = date_lists()
    temp_dir = os.path.expanduser(f'~/arcus_tasks_tmp/{split}/')
    os.makedirs(temp_dir, exist_ok=True)

    for year in years: 
        for month in months:
            print(f'processing {year}-{month}')
            gcs_jsonl_path = gcs_base_path + f'/datasets/identified_notes/padded/json/{year}-{month}.jsonl'
            gcs_tfrecord_file = gcs_base_path + f'/datasets/identified_notes/interleaved/tfrecords/{year}-{month}.tfrecords'
            jsonl_to_tfrecord_one_file_split(gcs_jsonl_path, gcs_tfrecord_file, temp_dir)

def convert_stragglers(): 
    from collections import OrderedDict
    straggler_dict = OrderedDict({
        '2013': 9,
        '2011': 10,
        '2014': 9,
        '2017': 11,
        '2005': 12, 
        '2006': 11, 
        '2004': 12, 
        '2008': 11
    })
    gcs_base_path = "gs://scit1565-pedsllm-b5-east5" # note no trailing fwd slash   
    split = int(os.getenv('SPLIT_ID'))
    s_ix = split - 1 # splits are not zero-indexed 
    year = list(straggler_dict.keys())[s_ix]
    years = [year]
    months = ["{:02d}".format(m) for m in range(straggler_dict[year], 13)]
    base_temp_folder = os.path.expanduser(f'~/arcus_tasks_tmp/')
    os.makedirs(base_temp_folder, exist_ok=True)
  

    # Outer context manager handles the temp directory
    with tempfile.TemporaryDirectory(prefix=f"split_{split}", dir=base_temp_folder) as temp_dir:
        for year in years: 
            for month in months:
                print(f'processing {year}-{month}')
                gcs_jsonl_path = gcs_base_path + f'/datasets/identified_notes/padded/json/{year}-{month}.jsonl'
                gcs_tfrecord_file = gcs_base_path + f'/datasets/identified_notes/interleaved/tfrecords/{year}-{month}.tfrecords'
                jsonl_to_tfrecord_one_file_split(gcs_jsonl_path, gcs_tfrecord_file, temp_dir)

def convert_stragglers_p2(): 
    
    gcs_base_path = "gs://scit1565-pedsllm-b5-east5" # note no trailing fwd slash   
    split = int(os.getenv('SPLIT_ID'))
    dates = date_lists_split_years(split)
    
    base_temp_folder = os.path.expanduser(f'~/arcus_tasks_tmp/')
    os.makedirs(base_temp_folder, exist_ok=True)
    

    # Outer context manager handles the temp directory
    with tempfile.TemporaryDirectory(prefix=f"split_{split}", dir=base_temp_folder) as temp_dir:
        for date in dates: 
            year = date[0]
            month = date[1]
            print(f'processing {year}-{month}')
            gcs_jsonl_path = gcs_base_path + f'/datasets/identified_notes/padded/json/{year}-{month}.jsonl'
            gcs_tfrecord_file = gcs_base_path + f'/datasets/identified_notes/interleaved/tfrecords/{year}-{month}.tfrecords'
            jsonl_to_tfrecord_one_file_split(gcs_jsonl_path, gcs_tfrecord_file, temp_dir)

def convert_test(): 
    gcs_base_path = "gs://scit1565-pedsllm-b5-east5" # note no trailing fwd slash   
  
    years = ['2005']
    months = ['11']
    split = 1 
    base_temp_folder = os.path.expanduser(f'~/arcus_tasks_tmp/')
    os.makedirs(base_temp_folder, exist_ok=True)
  

    # Outer context manager handles the temp directory
    with tempfile.TemporaryDirectory(prefix=f"split_{split}", dir=base_temp_folder) as temp_dir:
        for year in years: 
            for month in months:
                print(f'processing {year}-{month}')
                gcs_jsonl_path = gcs_base_path + f'/datasets/identified_notes/padded/json/{year}-{month}.jsonl'
                gcs_tfrecord_file = gcs_base_path + f'/datasets/identified_notes/interleaved/tfrecords/{year}-{month}.tfrecords'
                jsonl_to_tfrecord_one_file_split(gcs_jsonl_path, gcs_tfrecord_file, temp_dir)

#{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}
#gs://scit1565-pedsllm-b5-east5/datasets/identified_notes/interleaved/tfrecords/2019-12_110-of-110.tfrecords
#gs://scit1565-pedsllm-b5-east5/datasets/identified_notes/interleaved/tfrecords/2019-12_110-of-110.tfrecords
#gs://scit1565-pedsllm-b5-east5/datasets/test_builder/1.0/test_builder-test.tfrecord-00001-of-00001
def create_metadata():
    """This function was used to create tfds metadata files for dataset datasets/notes/1.0/"""
    data_dir = 'gs://scit1565-pedsllm-b5-east5/datasets/notes/1.0/'
    features = tfds.features.FeaturesDict({
        'inputs': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),  
        'inputs_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'inputs_segmentation': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'targets_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        "targets_segmentation": tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        })

    #split_infos=[tfds.core.SplitInfo(name='train', shard_lengths=[256, 256], num_bytes=0)]

    split_infos = tfds.folder_dataset.compute_split_info_from_directory(
                                                                        data_dir=data_dir, 
                                                                        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}')

    tfds.folder_dataset.write_metadata(
        data_dir=data_dir,
        features=features,
        split_infos=split_infos,
        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}', 
        description="""Tokenized and padded to 8192. Llama3 tokenizer. 2000 through 2019. Up to 256 examples per shard. 
        Initially parsed with int64 when converting from json, but loaded with int32 via tfds metadata"""
    )

def create_metadata_combined():
    """This function was used to create tfds metadata files for dataset /datasets/notes_replay_combined/1.0/"""
    data_dir = 'gs://scit1565-pedsllm-b5-east5/datasets/notes_replay_combined/1.0/'
    features = tfds.features.FeaturesDict({
        'inputs': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),  
        'inputs_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'inputs_segmentation': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'targets_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        "targets_segmentation": tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        })

    #split_infos=[tfds.core.SplitInfo(name='train', shard_lengths=[256, 256], num_bytes=0)]

    split_infos = tfds.folder_dataset.compute_split_info_from_directory(
                                                                        data_dir=data_dir, 
                                                                        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}')

    tfds.folder_dataset.write_metadata(
        data_dir=data_dir,
        features=features,
        split_infos=split_infos,
        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}', 
        description="""Combined dataset of notes and replay. Tokenized and padded to 8192. Llama3 tokenizer. Prefixes of 
        files that were renamed and combined into this dataset: ['datasets/finetune/interleaved/tfrecords/', 'datasets/replay/interleaved/tfrecords/', 'datasets/identified_notes/interleaved/tfrecords/'] 
        Notes data, initially parsed with int64 when converting from json, but loaded with int32 via tfds metadata"""
    )

def create_test_metadata():
    data_dir = 'gs://scit1565-pedsllm-b5-east5/datasets/test_builder/1.0/'
    features = tfds.features.FeaturesDict({
        'inputs': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),  
        'inputs_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'inputs_segmentation': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        'targets_position': tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        "targets_segmentation": tfds.features.Tensor(shape=(8192,), dtype=tf.int32),
        })

    #split_infos=[tfds.core.SplitInfo(name='train', shard_lengths=[256, 256], num_bytes=0)]

    split_infos = tfds.folder_dataset.compute_split_info_from_directory(
                                                                        data_dir=data_dir, 
                                                                        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}')

    tfds.folder_dataset.write_metadata(
        data_dir=data_dir,
        features=features,
        split_infos=split_infos,
        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}', 
        description=""
    )

def test_builder(): 
    builder = tfds.builder_from_directory('gs://scit1565-pedsllm-b5-east5/datasets/test_builder/1.0/')
    ds = builder.as_dataset(split='train')

def build_split_info(): 
    split_info = tfds.folder_dataset.compute_split_info_from_directory(
                                                                        data_dir='gs://scit1565-pedsllm-b5-east5/datasets/test_builder/1.0/', 
                                                                        filename_template='{DATASET}-{SPLIT}.{FILEFORMAT}-{SHARD_X_OF_Y}')
    print(split_info)

def main():
    #convert_all_notes()    
    #convert_stragglers()
    #create_metadata()
    #build_split_info()
    #test_builder()
    #convert_stragglers_p2()
    #rename_records()
    #create_metadata()
    #create_test_metadata()
    create_metadata_combined()

if __name__ == "__main__":
    main()
    

