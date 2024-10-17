conda run --no-capture-output -n python3.10.12 maxtext/MaxText/llama_mistral_mixtral_orbax_to_hf.py maxtext/MaxText/configs/base.yml base_output_directory=gs://scit1565-pedsllm-b5-def/tmp load_parameters_path=gs://scit1565-pedsllm-b5-def/v6e-llama3.1-8b-instruct/checkpoints/4000/items model_name=llama3.1-8b hardware=gpu hf_model_path=/home/zhaox4/tmp

