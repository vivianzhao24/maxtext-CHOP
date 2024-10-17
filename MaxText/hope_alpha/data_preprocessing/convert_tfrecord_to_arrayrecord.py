from apache_beam.options import pipeline_options
from array_record.beam.pipelines import convert_tf_to_arrayrecord_gcs
import os


PROJECT = os.getenv('PROJECT_ID')
REGION = os.getenv('ZONE')

## Set input and output patterns as specified
input_pattern = 'gs://scit1565-pedsllm-b5-south1/datasets/toy_dataset/tfrecord-data/*.tfrecords'
output_path = 'gs://scit1565-pedsllm-b5-south1/datasets/toy_dataset/array-records/'

args = {'input': input_pattern, 'output': output_path}

## Set pipeline options and uncomment in main() to run in Dataflow
pipeline_options = pipeline_options.PipelineOptions(
    #runner='DataflowRunner',
    project=PROJECT,
    region=REGION,
    #requirements_file='requirements.txt'
)


def main():
  convert_tf_to_arrayrecord_gcs(
      args=args,
      pipeline_options=pipeline_options
  )[0].run()

if __name__ == '__main__':
  main()