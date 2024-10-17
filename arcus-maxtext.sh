#!/bin/bash
#######################
## ARCUS PRE-CONFIG  ##
#######################
set -ex
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_SUSPEND=1
export NEEDRESTART_MODE=l
### Add host records for DNS override 
echo "199.36.153.8 us-east4-apt.pkg.dev" | sudo tee -a /etc/hosts
echo "199.36.153.8 packages.cloud.google.com" | sudo tee -a /etc/hosts
echo "199.36.153.8 us-east4-python.pkg.dev" | sudo tee -a /etc/hosts
echo "199.36.153.8 storage.googleapis.com" | sudo tee -a /etc/hosts
### auto approve app restarts
sudo sed -i "38s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
### Remove other apt repos
sudo touch /etc/apt/sources.list.d/txt.list
sudo rm /etc/apt/sources.list.d/*
### Load apt gpg key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
curl https://us-east4-apt.pkg.dev/doc/repo-signing-key.gpg | sudo apt-key add - && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
### Overwrite apt file 
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list
echo 'deb https://packages.cloud.google.com/apt apt-transport-artifact-registry-stable main' | sudo tee -a /etc/apt/sources.list
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list
### Install apt-transport-artifact-registry
sudo apt update
sudo apt install -y apt-transport-artifact-registry google-cloud-cli 
### Setup arcus-apt-packages repo
echo "deb ar+https://us-east4-apt.pkg.dev/projects/arcus-kubernetes arcus-apt-packages main" | sudo tee -a /etc/apt/sources.list
sudo apt update && sudo apt upgrade -y && sudo apt install -y jq libjq1 libonig5 pre-commit && sudo apt auto-remove -y
#######################
### SETUP Python
cat <<EOF > .pypirc 
# Insert the following snippet into your .pypirc
[distutils]
index-servers =
    arcus-python-packages
[arcus-python-packages]
repository: https://us-east4-python.pkg.dev/arcus-kubernetes/arcus-python-packages/
EOF
mkdir -p ~/.config/pip
cat <<EOF > ~/.config/pip/pip.conf
# Insert the following snippet into your pip.conf
[global]
index-url = https://us-east4-python.pkg.dev/arcus-kubernetes/arcus-python-packages/simple/
EOF
mkdir py
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py \
    --local-filename=keyring-25.2.1-py3-none-any.whl \
    keyring/keyring-25.2.1-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=keyrings.google_artifactregistry_auth-1.1.2-py3-none-any.whl \
    keyrings-google-artifactregistry-auth/keyrings.google_artifactregistry_auth-1.1.2-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=pluggy-1.5.0-py3-none-any.whl \
    pluggy/pluggy-1.5.0-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=cachetools-5.3.3-py3-none-any.whl \
    cachetools/cachetools-5.3.3-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=pyasn1-0.6.0-py2.py3-none-any.whl \
    pyasn1/pyasn1-0.6.0-py2.py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=rsa-4.9-py3-none-any.whl \
    rsa/rsa-4.9-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=jaraco.context-5.3.0-py3-none-any.whl \
    jaraco-context/jaraco.context-5.3.0-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=jaraco.classes-3.4.0-py3-none-any.whl  \
    jaraco-classes/jaraco.classes-3.4.0-py3-none-any.whl 
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=jaraco.functools-4.0.1-py3-none-any.whl \
    jaraco-functools/jaraco.functools-4.0.1-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=backports.tarfile-1.2.0-py3-none-any.whl \
    backports-tarfile/backports.tarfile-1.2.0-py3-none-any.whl 
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=importlib_metadata-7.2.1-py3-none-any.whl \
    importlib-metadata/importlib_metadata-7.2.1-py3-none-any.whl
gcloud artifacts files download \
    --project=arcus-kubernetes \
    --location=us-east4 \
    --repository=arcus-python-packages \
    --destination=py  \
    --local-filename=google_auth-2.32.0-py2.py3-none-any.whl  \
    google-auth/google_auth-2.32.0-py2.py3-none-any.whl 
pip install py/*
rm -rf py