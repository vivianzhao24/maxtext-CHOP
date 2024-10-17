import os
from input_pipeline._tfds_data_processing import make_tfds_iterator
import pyconfig 


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

def _get_train_iterator(self):
    train_iter, eval_iter = _tfds_data_processing.make_tfds_iterator(
      self.config, self.mesh, self.process_indices)
    return train_iter, eval_iter

def test_train_ds(self):
    expected_shape = [jax.device_count(), self.config.max_target_length]
    # For training we pack multiple short examples in one example.
    # *_position and *_segmentation indicate the boundaries.
    batch = next(self.train_iter)
    self.assertEqual(
        {k: list(v.shape) for k, v in batch.items()},
        {
            "inputs": expected_shape,
            "inputs_position": expected_shape,
            "inputs_segmentation": expected_shape,
            "targets": expected_shape,
            "targets_position": expected_shape,
            "targets_segmentation": expected_shape,
        },
    )

def test_tf_dataset():
  
  tf.data.experimental.enable_debug_mode() #enable eager execution as opposed to graph; or would need to start with a session
  dataset_name = "gs://scit1565-pedsllm-b5-south1/datasets/toy_dataset/tfrecord-data/"
  data_split='train'
  shuffle_files = False
  ds = get_datasets(
    dataset_name,
    data_split,
    shuffle_files,
    read_config=None,
    from_tfrecords=True,)
  parsed_ds = ds.map(decode_fn)
  print(type(parsed_ds))
  for raw_record in parsed_ds.take(500):
    print(repr(raw_record))


if __name__ == "__main__": 
  pyconfig.initialize(["MaxText/configs/base.yml"])
  pyconfig._config._load_config("/home/donatim/maxtext/MaxText/configs/hope_alpha.yml")
  config = pyconfig.config
  print(config.tokenize_train_data)
  
  # Set this to True to run the model on CPU only.
  USE_CPU_ONLY = True

  flags = os.environ.get("XLA_FLAGS", "")
  if USE_CPU_ONLY:
      flags += " --xla_force_host_platform_device_count=8"  # Simulate 8 devices
      # Enforce CPU-only execution
      os.environ["CUDA_VISIBLE_DEVICES"] = ""
  


