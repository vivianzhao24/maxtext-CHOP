#!/bin/bash

# Example usage: 
    # Setup full v5e pod, for use with tfds, in nightly mode: 
        # 1. export_envs_v5e_256_tpus
        # 2. requisition_v5e_resources
        # 3. initialize_multi_host_nightly
        # 4. patch_maxtext_scripts

    # The following setups for grain and single host have not been tested with the latest setup.  Use as reference point only prior to re-testing. 
    # Setup full v5e pod, for use with grain, in nightly mode: 
        # 1. export_envs_v5e_256_tpus
        # 2. requisition_v5e_resources
        # 3. initialize_multi_host_nightly 
        # 4. mount_gcs_multi_host
        # 5. patch_maxtext_scripts
    # Singlehost setup for use with tfds: 
        # 1. export_envs_v5e_8_tpus
        # 2. requisition_resources
        # 3. initialize_single_host
        # 4. ssh_to_single_host
    
    # When finished with resources, run release_resources 


# Notes 
    # Use sync_maxtext_single_host with filenames passed to function to sync any local changes to maxtext after setup. 
    # A sync_maxtext_multihost is not needed to sync any changes to maxtext because the multihost data runner will scp the maxtext folder each time it is run. 
    # conda env is no longer needed and can be removed in next refactor 

export USER=zhaox4
export CONDA_ENV="python3.10.12"
export MAXTEXT_DIR="$HOME/maxtext/" # note the inclusion of the trailing forward slash 

# Note: export_v6e_32_preview_envs() is only set only for trillium preview testing. The env may be subject to change later.12

export_trillium_preview_envs(){
    export PROJECT_ID=scit1565-pedsllm-b5
    export ACCELERATOR_TYPE=v6e-8
    export ZONE=us-east5-b
    export RUNTIME_VERSION=v2-alpha-tpuv6e
    export NODE_COUNT=32
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com
    export TPU_NAME="${PROJECT_ID}-${ACCELERATOR_TYPE}"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-east5/subnetworks/scit1565-pedsllm-b5-east5
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}

export_envs_v6e_16_slices(){
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v6e-8
    export ZONE=us-east5-b 
    export RUNTIME_VERSION=v2-alpha-tpuv6e
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export NODE_COUNT=16
    export TPU_NAME="${USER}-$ACCELERATOR_TYPE-$NODE_COUNT"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-east5/subnetworks/scit1565-pedsllm-b5-east5
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/${ZONE}/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}


export_envs_v5e_8_tpus(){
    # be sure to change user id in TPU_NAME 
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v5litepod-8
    export ZONE=us-central1-a 
    export RUNTIME_VERSION=v2-alpha-tpuv5-lite
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export TPU_NAME="${USER}-v5litepod-8"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-central1-a/subnetworks/scit1565-pedsllm-b5-central1
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/us-central1-a/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}

export_envs_v5e_16_tpus(){
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v5litepod-16
    export ZONE=us-south1-a 
    export RUNTIME_VERSION=v2-alpha-tpuv5-lite
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export TPU_NAME="${USER}-v5litepod-16"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-south1-a/subnetworks/scit1565-pedsllm-b5-south1
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/${ZONE}/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}

export_envs_v5e_64_tpus(){
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v5litepod-64
    export ZONE=us-south1-a 
    export RUNTIME_VERSION=v2-alpha-tpuv5-lite
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export TPU_NAME="${USER}-v5litepod-64"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-south1-a/subnetworks/scit1565-pedsllm-b5-south1
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/${ZONE}/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}

export_envs_v5e_128_tpus(){
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v5litepod-128
    export ZONE=us-south1-a 
    export RUNTIME_VERSION=v2-alpha-tpuv5-lite
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export TPU_NAME="${USER}-v5litepod-128"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-south1-a/subnetworks/scit1565-pedsllm-b5-south1
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/${ZONE}/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}

export_envs_v5e_256_tpus(){
    export PROJECT_ID=scit1565-pedsllm-b5 
    export ACCELERATOR_TYPE=v5litepod-256
    export ZONE=us-south1-a 
    export RUNTIME_VERSION=v2-alpha-tpuv5-lite
    export SERVICE_ACCOUNT=scit1565-pedsllm-b5@scit1565-pedsllm-b5.iam.gserviceaccount.com 
    export TPU_NAME="${USER}-v5litepod-256"
    export QUEUED_RESOURCE_ID=$TPU_NAME
    export NETWORK=projects/arcus-vpc-master/global/networks/arcus-master-vpc	\
    export SUBNETWORK=projects/arcus-vpc-master/regions/us-south1-a/subnetworks/scit1565-pedsllm-b5-south1
    export QUEUED_RESOURCE_NAME=projects/scit1565-pedsllm-b5/locations/${ZONE}/queuedResources/${TPU_NAME}
    gcloud config set project $PROJECT_ID --quiet
    gcloud config set compute/zone $ZONE --quiet
}


# Need to pass in "--best-effort" as argument if want to use spot requisition
requisition_v6e_resources(){
    if [[ "$#" -eq 1 && "$1" == "--best-effort" ]]; then 
        best_effort_flag="$1"
    fi
    echo $best_effort_flag

    gcloud alpha compute tpus queued-resources create ${QUEUED_RESOURCE_ID} \
        --node-count=${NODE_COUNT} \
        --node-prefix ${TPU_NAME} \
        --project ${PROJECT_ID} \
        --network ${NETWORK} \
        --subnetwork ${SUBNETWORK} \
        --zone ${ZONE} \
        --accelerator-type ${ACCELERATOR_TYPE} \
        --runtime-version ${RUNTIME_VERSION} \
        --service-account ${SERVICE_ACCOUNT} \
        --internal-ips \
        ${best_effort_flag:+"$best_effort_flag"}

    # Loop until the status is ACTIVE"
    while true; do
        status=$(gcloud compute tpus queued-resources list --filter=name=${QUEUED_RESOURCE_NAME} | awk 'NR==2 {print $5}')
        if echo "$status" | grep -q "ACTIVE"; then
            echo "Host is active. Proceeding to next command."
            break
        else
            echo $status
            echo "Waiting for host to become active..."
        fi
        sleep 5
    done
}

requisition_v5e_resources(){
    if [[ "$#" -eq 1 && "$1" == "--best-effort" ]]; then 
        best_effort_flag="$1"
    fi
    echo $best_effort_flag

    gcloud alpha compute tpus queued-resources create ${QUEUED_RESOURCE_ID} \
        --node-id ${TPU_NAME} \
        --project ${PROJECT_ID} \
        --network ${NETWORK} \
        --subnetwork ${SUBNETWORK} \
        --zone ${ZONE} \
        --accelerator-type ${ACCELERATOR_TYPE} \
        --runtime-version ${RUNTIME_VERSION} \
        --service-account ${SERVICE_ACCOUNT} \
        --internal-ips \
        ${best_effort_flag:+"$best_effort_flag"}

    # Loop until the status is ACTIVE"
    while true; do
        status=$(gcloud compute tpus queued-resources list --filter=name=${QUEUED_RESOURCE_NAME} | awk 'NR==2 {print $5}')
        if echo "$status" | grep -q "ACTIVE"; then
            echo "Host is active. Proceeding to next command."
            break
        else
            echo $status
            echo "Waiting for host to become active..."
        fi
        sleep 5
    done
}

release_resources(){
    yes | gcloud alpha compute tpus tpu-vm delete ${TPU_NAME} --project=${PROJECT_ID} --zone=${ZONE} --quiet
    yes | gcloud compute tpus queued-resources delete ${TPU_NAME}
}

ssh_to_single_host(){
    gcloud alpha compute tpus tpu-vm ssh $TPU_NAME --zone=$ZONE  --internal-ip        
}


ssh_to_multi_host_worker1(){
    gcloud alpha compute tpus tpu-vm ssh $TPU_NAME --zone=$ZONE  --internal-ip  --worker 1       
}


# Deprecated
setup_multi_host(){
    cd /home/donatim/maxtext
    python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="
    sudo apt update && sudo apt install -y pre-commit;
    export PATH='/home/sa_112413943341569390945/.local/bin:$PATH';
    bash setup.sh"
}

initialize_single_host(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "initialize_single_host scp's pip wheels and maxtext folder to single host before running arcus-maxtext.sh and setup.sh"
    else
        gcloud alpha compute tpus tpu-vm scp /mnt/arcus/lab/shared/maxtext_pip_wheels/ $TPU_NAME:~/ --recurse
        gcloud alpha compute tpus tpu-vm scp "$MAXTEXT_DIR" $TPU_NAME:~/ --recurse    
        gcloud alpha compute tpus tpu-vm ssh $TPU_NAME --command="export PATH=\'/home/sa_112413943341569390945/.local/bin:\$PATH\'; bash arcus-maxtext.sh; bash setup.sh"
    fi

}

initialize_multi_host(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "initialize_multi_host scp's pip wheels and maxtext folder before running arcus-maxtext.sh and setup.sh"
    else
        source /opt/conda/bin/activate ${CONDA_ENV}
        cd "$MAXTEXT_DIR"
         # 'Patch' requirements.txt 
        python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="export PATH=\"/home/sa_112413943341569390945/.local/bin:\$PATH\";bash arcus-maxtext.sh"
        python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="export PATH=\"/home/sa_112413943341569390945/.local/bin:\$PATH\";bash setup.sh"
    fi
}

initialize_multi_host_nightly(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "initialize_multi_host scp's pip wheels and maxtext folder before running arcus-maxtext.sh and setup.sh"
    else
        source /opt/conda/bin/activate ${CONDA_ENV}
        cd "$MAXTEXT_DIR"
        # 'Patch' requirements.txt and setup.sh
        cat ./MaxText/hope_alpha/patches/requirements_from_directory.txt > ./requirements.txt
        cat ./MaxText/hope_alpha/patches/setup_nightly.sh > ./setup.sh
        gcloud alpha compute tpus tpu-vm scp /mnt/arcus/lab/shared/maxtext_pip_wheels/maxtext_pip_wheels_main/  $TPU_NAME:~/ --recurse --worker=all
        python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="export PATH=\"/home/sa_112413943341569390945/.local/bin:\$PATH\";bash arcus-maxtext.sh"
        python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="export PATH=\"/home/sa_112413943341569390945/.local/bin:\$PATH\";bash setup.sh MODE=nightly"
    fi
}

patch_maxtext_scripts(){
    cat ${MAXTEXT_DIR}MaxText/hope_alpha/patches/_tfds_data_processing_from_directory.py > ${MAXTEXT_DIR}MaxText/input_pipeline/_tfds_data_processing.py
    cat ${MAXTEXT_DIR}MaxText/hope_alpha/patches/max_utils_init_jax_dist.py > ${MAXTEXT_DIR}MaxText/max_utils.py
    cat ${MAXTEXT_DIR}MaxText/hope_alpha/patches/checkpointing_checkpoint_iterator.py > ${MAXTEXT_DIR}MaxText/checkpointing.py
}

mount_gcs_multi_host(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo ""
    else
        cd "$MAXTEXT_DIR"
        python3 multihost_runner.py --TPU_PREFIX=$TPU_NAME --COMMAND="export PATH=\"/home/sa_112413943341569390945/.local/bin:\$PATH\";bash setup_gcsfuse.sh DATASET_GCS_BUCKET=gs://scit1565-pedsllm-b5-south1  MOUNT_PATH=/home/sa_112413943341569390945/gcs-bucket"
    fi
}

arcus_single_host(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "arcus_single_host runs arcus-maxtext.sh on single host"
    else
        gcloud alpha compute tpus tpu-vm ssh $TPU_NAME --command="bash arcus-maxtext.sh"
    fi
}

setup_single_host(){
     if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "setup_single_host runs setup.sh on single host"
    else
        gcloud alpha compute tpus tpu-vm ssh $TPU_NAME --command="cd $MAXTEXT_DIR; bash setup.sh"
    fi
}

sync_maxtext_single_host(){
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then 
        echo "sync_maxtext_single_host syncs files passed to function from the local ~/maxtext/ folder to the ~/maxtext/ folder on the remote single host"
    else
        for file in "$@"; do
            gcloud alpha compute tpus tpu-vm scp "${MAXTEXT_DIR}${file}" $TPU_NAME:"${MAXTEXT_DIR}${file}"
        done
    fi

}

