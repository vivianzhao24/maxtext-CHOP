# Training Using Preprocessed Data

## Patches to the Upstream Repo

Changes to the maxtext repo are kept separate in a patches folder. It is setup this way in order to keep changes isolated, hopefully allowing for fetching upstream updates without necessitating complicated merging. As of now the patches are deployed by overwriting files (via bash functions).  In the future it may make more sense to construct actual git patches, automatic rules, a submodule, or branches holding custom changes. 
## Setting up Multi Host TPUs 

MaxText works more seamlessly with a GKE cluster.  Since it is not being run on GKE, it requires additional setup, and some adjustments may be required (see jax distributed initialization as an example). 

In order to prepare a TPU cluster for training, follow the five main steps below (with an additional step if working with the grain pipeline.)  The bash functions for these steps are contained in the file `https://github.research.chop.edu/Ian-Campbell-Lab/maxtext/edit/main/MaxText/hope_alpha/setup_vms.sh` The functions are often different between v5e and v6e setups. 

Change `USER` and `CONDA_ENV` variables  in the `setup_vms.sh` file. Currently, activating a conda environment is not necessary, but this step is built into the script in case `multihost_runner.py` is ever updated to require additional python modules.  
### Step 1. Export environmental variables 

- v5e
	- choose the function that corresponds to the number of tpus required. Possible configurations are 8, 16, 64, 128, or 256 TPUs
		- Function: `export_envs_v5e_<Number of TPUs>_tpus`
- v6e 
	- choose the function that corresponds to the number of slices required. Possible configurations are 16 or 32 slices. Each slice contains 8 TPUs. 
	- Function: `export_envs_v6e_<Number of Slices>_slices`

Many commands, such as requisitioning and releasing the resources, require the environmental variables to be set consistently, so be sure to re-run the export function when opening a new bash terminal. 
### Step 2. Requisition the resources 

- The function to requisition the TPUs should request the resources and loop a status check until the resources are requisitioned and active 
- Pass `"--best-effort"` to the respective function if requesting spot (preemptible) instances. 
- v5e 
	- Function: `requisition_v5e_resources`
- v6e 
	- Function: `requisition_v6e_resources`

### Notes on steps 3 & 4

For each TPU type, steps 1 and 2 are handled separately by distinct functions; but steps 3 & 4 are handled within a single function. Below are steps 3 & 4 broken out, followed by the functions to run.   

The python file `multihost_runner.py` is used to run commands on every TPU host. Of note, whenever this file is run using python it will scp the maxtext folder containing the file to the TPU hosts.  So any changes made to the local maxtext directory will be reflected on the TPUs each time `multihost_runner.py` is executed.

### Step 3. Setup TPUs to function with the firewall active 

- The stable Arcus setup should utilize the artifact registry to get necessary pip wheels for the TPUs.  However, because the package versions have not yet been solidified during the testing process, there is an additional step to send different versions of downloaded wheels to the TPUs, using SCP. 
	- Long term, setting up TPUs to function with the firewall active will only require one step: 
		- Use `mulithost_runner.py` to run `arcus-maxtext.sh` on each TPU host. 
	- Currently, setting up TPUs to function with the firewall active requires two steps: 
		- Use `gcloud alpha compute tpus tpu-vm scp` to scp pip wheels to each TPU host
		- Use `mulithost_runner.py` to run `arcus-maxtext.sh` on each TPU host. 

### Step 4. Setup TPUs to run MaxText
This step involves installing MaxText requirements on the TPU hosts. 
- Long term, when using the artifact registry: 
	- use `mulithost_runner.py` to run `setup.sh` on each TPU host. 
- Currently: 
	- 'Patch' file(s) in order to facilitate installation of requirements from downloaded wheels: 
		- edit the `requirements.txt` file to point pip to a links folder and remove URL references. 
		- If setting up in nightly mode, edit the `setup.sh` file to install nightlies from a links folder. 
	- use `mulithost_runner.py` to run `setup.sh` on each TPU host. 
	
### Executing Steps 3 & 4: 

- Nightly mode: 
	- Run the following bash function (contained in the `step_vms.sh` file):`initialize_multi_host_nightly
- Default: 
	- Run the following bash function (contained in the `step_vms.sh` file):`initialize_multi_host

### Step 5. Patch MaxText Scripts
- Some MaxText scripts need to be edited in order to 1) load data from a directory into a tfds builder, as opposed to loading a registered dataset by name; 2) force initialization of jax.distributed (this may be necessary because maxtext is not being run an GKE); and 3) checkpoint the data iterator.  
- In order to incorporate these patches run the following bash function (contained in the `step_vms.sh` file): `patch_maxtext_scripts`
### Releasing resources: 
- Run the following bash function (contained in the `step_vms.sh` file): `release_resources
### Putting it all together

- Setting up 256 v5e's in nightly mode
	- Clone maxtext to your home directory. Do not rename the maxtext folder. 
	- Change `USER` and `CONDA_ENV` variables  in the `~/maxtext/MaxText/hope_alpha/setup_vms.sh` file
	- In the terminal run the following commands: 
		- `source ~/maxtext/MaxText/hope_alpha/setup_vms.sh  
		- `export_envs_v5e_256_tpus`
		- `requisition_v5e_resources`
		- `initialize_multi_host_nightly`
		- `patch_maxtext_scripts`
- Release resources following training or testing: 
	- `release_resources
### Training

### Additional Notes
Recommend running initialization and training commands from the terminal app in Arcus. Using the the terminal in the VS code editor app appeared to cause issues with database locking due to parallel requests. (Though this has not been confirmed). 

Note that the 8 - TPU configuration is a single host configuration, while the larger configurations are all multi-host.  Single host is setup in central1, while Multi-host is setup in south1