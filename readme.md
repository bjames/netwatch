# NetWatch

Periodically run show commands on Cisco IOS or NXOS devices and print the output to the screen or write it to a file.

## Installation

Requires python 3+. I strongly suggest creating a new virtual environment for use with this script. I broadly cover this here.

1. install virtualenv if it's not already installed `python -m pip install virtualenv`

2. create a new virtualenv `python -m virtualenv venv`

3. clone the repository `git clone https://github.com/bjames/netwatch`

4. activate the virtualenv
   * Linux/OS X `source ./venv/bin/activate`
   * Windows `venv\Scripts\activate`

5. install the required libraries `python -m pip install -r netwatch/requirements.txt'

## Usage

1. Edit the YAML file, note that anything defined under the default section can be overridden on a per-device basis. The YAML file included here demonstrates overridding the device_type, port and command list.

2. This script makes use of the multiprocessing library's Pool.map() function. This allows the script to run commands on multiple devices at the same time. This means that as long as you give the script enough threads (one per device), the commands will be run on the device at roughly the same time. 

3. If you have __file_output__ set to true, the script creates one file per device with command output and timestamps. The script appends to the file at the end of each iteration, so if the script dies or gets stopped, the results will not be lost. 
