## Arcus - MaxText
- ### Raw Data: 
	- Directory: `mnt/arcus/data/AG-5007`
	- Format:  json; each file contains one cohort. each cohort is one  birth month/year
- ### Processing: 
	- #### Process from raw json to reformatted and tokenized jsonl
		- Processing pipeline includes metadata-tokenize-split-pack-pad
		- Git repo/branch: 
			- `https://github.research.chop.edu/Ian-Campbell-Lab/Hope-Alpha/tree/llama31_data_pipeline`
		- script: 
			- `Hope-Alpha/src/scripts/data_pipeline/create_packed_maxtext_dataset.py`
		- Arcus tasks submission (submit 2 tasks, 12 years each, changing only the starting year in the 2nd submitted script)
			- ```lab-tasks submit-script --name <submission_name> --path ~/Hope-Alpha/src/scripts/data_pipeline/create_packed_maxtext_dataset.py --cpu 9 --memory 200 --split 4 --parallel 4```

	- ####  Further process jsonl to sharded tfrecords (max 256 examples per shard) 
		- Git repo (main branch): `https://github.research.chop.edu/Ian-Campbell-Lab/maxtext.git`
		- script: `maxtext/MaxText/hope_alpha/convert_jsonl_to_tfrecord.py`
		- function: `jsonl_to_tfrecord_one_file_split`
	- #### Rename files for use with tfds: 
		- script: `maxtext/MaxText/hope_alpha/convert_jsonl_to_tfrecord.py`
		- dataset: `datasets/notes/1.0/`
			- function: `rename_records`
		- dataset: `datasets/notes_replay_combined/1.0/`
			- function: `rename_records_combined`		
	- #### Create metadata  json files needed by tfds builder: 
		- script: `maxtext/MaxText/hope_alpha/convert_jsonl_to_tfrecord.py`
		- dataset: `datasets/notes/1.0/`
			- function: `create_metadata`
		- dataset: `datasets/notes_replay_combined/1.0/`
			- function: `create_metadata_combined`		
	- #### Load tfrecords into tfds builder: 
		- Edit maxtext input pipeline file:
			-  file: `maxtext/MaxText/input_pipeline/_tfds_data_processing.py`
			- Change ds_builder assignment to: 
				- `ds_builder = tfds.builder_from_directory('gs://scit1565-pedsllm-b5-south1/datasets/notes/1.0/')`
		- Note this is handled by the `patch_maxtext_scripts` function in the setup_vms.sh script. 

