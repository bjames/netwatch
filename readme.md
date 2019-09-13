## Implementation Goals

1. Execution should take place on each device simultaneously to get a full picture of the network at a single moment in time.
2. The script should be reusable without any modifications to the script itself.
3. The output should include accurate timestamps so we can correlate events across multiple devices.
4. Output should be written to a file each time the main loop executes, that way if the script is stopped or dies we don't lose the data up to that point.
5. The script should be able to complete it's task without using task scheduler or Cron. As these require configuration to take place outside of the script.


## Installation

Requires python 3+. I strongly suggest creating a new virtual environment for use with this script. I broadly cover this here.

1. install virtualenv if it's not already installed `python -m pip install virtualenv`

2. create a new virtualenv `python -m virtualenv venv`

3. clone the repository `git clone https://github.com/bjames/netwatch`

4. activate the virtualenv
   * Linux/OS X `source ./venv/bin/activate`
   * Windows `venv\Scripts\activate`

5. install the required libraries `python -m pip install -r netwatch/requirements.txt'

## Configuration

In the YAML file, anything defined under the default section can be overridden on a per-device basis. The YAML file below demonstrates overriding the device_type and command list. 

```
# Number of devices to run commands on in parallel
threads: 4
# Time to sleep in between iterations (seconds)
sleep_time: 300
# maximum iterations (set to 0 to repeat forever)
max_iter: 288
# If true, the results are output to one file per device
file_output: true
# If true, the results are printed to the screen
print_output: true
# default settings that may be overridden on a per device basis
default:
  # commands to run
  commands:
    - show int status
    - show cdp neighbors
  # cisco_ios or cisco_nxos
  device_type: cisco_ios
  port: 22
# list devices and device specific config
device_list:
 - hostname: IOS-SWITCH-1A
 - hostname: NXOS-SWITCH-1A
   device_type: cisco_nxos
   commands: 
    - show vlan brief
    - show ip route
```

* This configuration runs `show int status` followed by `show cdp neighbors` on IOS-SWITCH-1A and `show vlan brief` followed by `show ip route` on NXOS-SWITCH-1A. The script runs every 300 seconds and repeats 288 times or once every 5 minutes for 24 hours. 

* The script uses python's multiprocessing library's Pool.map() function. This allows the script to run commands on multiple devices at the same time. As long as you give the script enough threads (one per device), the command execution will start on each device at roughly the same time. In the above configuration, we've told the script it can spawn up to 4 threads, but in this case only 2 threads will actually be used. I've used 16 threads on Linux VM with 2 cores and 4GB of RAM without any performance degradation, but your mileage my vary. 

* You can read more about how I handle concurrency [here](https://neverthenetwork.com/notes/automation_concurrency/) and how I handle script configuration [here](https://neverthenetwork.com/notes/automation_config/).

## Usage

1. Run the script `python ./netwatch.py`. You can also specify a configuration file `python ./netwatch.py myconfig.yaml`.
	* The script will validate your credentials against the first device in the device list before execution begins. This is done to prevent account lockouts.
2. The script will run until it is either stopped or the `max_iter` value is reached. If `file_output` is set to `true`, the script creates one log file per device and appends the output to the log files following each iteration.

## Example Output

```
!!!!!!! show int status on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:35:32.990650


--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
mgmt0         DO NOT TOUCH CONFI connected routed    full    1000    --         

--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
Eth1/1        --                 connected trunk     full    1000    10g        
Eth1/2        --                 connected trunk     full    1000    10g        
Eth1/3        --                 connected 1         full    auto    10g        
Eth1/4        --                 connected 1         full    auto    10g        
Eth1/5        L3 Link            connected routed    full    1000    10g        
< REDACTED FOR BREVITY>  
Po11          --                 connected trunk     full    1000    --         
Lo1           --                 connected routed    auto    auto    --         
Lo100         --                 connected routed    auto    auto    --         
Vlan1         --                 down      routed    auto    auto    --
Vlan100       mgmt svi - DEMO PL connected routed    auto    auto    --
Vlan101       prod svi - DEMO PL connected routed    auto    auto    --
Vlan102       dev svi - DEMO PLE connected routed    auto    auto    --
Vlan103       test svi - DEMO PL connected routed    auto    auto    --
Vlan104       security svi - DEM connected routed    auto    auto    --
Vlan105       iot svi - DEMO PLE connected routed    auto    auto    --

!!!!!!! show cdp neighbors on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:35:33.895258

Capability Codes: R - Router, T - Trans-Bridge, B - Source-Route-Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater,
                  V - VoIP-Phone, D - Remotely-Managed-Device,
                  s - Supports-STP-Dispute

Device-ID          Local Intrfce  Hldtme Capability  Platform      Port ID

Total entries displayed: 0

!!!!!!! show int status on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:35:56.499806


--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
mgmt0         DO NOT TOUCH CONFI connected routed    full    1000    --         

--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
Eth1/1        --                 connected trunk     full    1000    10g        
Eth1/2        --                 connected trunk     full    1000    10g        
Eth1/3        --                 connected 1         full    auto    10g        
Eth1/4        --                 connected 1         full    auto    10g        
Eth1/5        L3 Link            connected routed    full    1000    10g        
< REDACTED FOR BREVITY>    
Po11          --                 connected trunk     full    1000    --         
Lo1           --                 connected routed    auto    auto    --         
Lo100         --                 connected routed    auto    auto    --         
Vlan1         --                 down      routed    auto    auto    --
Vlan100       mgmt svi - DEMO PL connected routed    auto    auto    --
Vlan101       prod svi - DEMO PL connected routed    auto    auto    --
Vlan102       dev svi - DEMO PLE connected routed    auto    auto    --
Vlan103       test svi - DEMO PL connected routed    auto    auto    --
Vlan104       security svi - DEM connected routed    auto    auto    --
Vlan105       iot svi - DEMO PLE connected routed    auto    auto    --

!!!!!!! show cdp neighbors on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:35:57.305606

Capability Codes: R - Router, T - Trans-Bridge, B - Source-Route-Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater,
                  V - VoIP-Phone, D - Remotely-Managed-Device,
                  s - Supports-STP-Dispute

Device-ID          Local Intrfce  Hldtme Capability  Platform      Port ID

Total entries displayed: 0

!!!!!!! show int status on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:18.511021


--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
mgmt0         DO NOT TOUCH CONFI connected routed    full    1000    --         

--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
Eth1/1        --                 connected trunk     full    1000    10g        
Eth1/2        --                 connected trunk     full    1000    10g        
Eth1/3        --                 connected 1         full    auto    10g        
Eth1/4        --                 connected 1         full    auto    10g        
Eth1/5        L3 Link            connected routed    full    1000    10g        
< REDACTED FOR BREVITY>  
Po11          --                 connected trunk     full    1000    --         
Lo1           --                 connected routed    auto    auto    --         
Lo100         --                 connected routed    auto    auto    --         
Vlan1         --                 down      routed    auto    auto    --
Vlan100       mgmt svi - DEMO PL connected routed    auto    auto    --
Vlan101       prod svi - DEMO PL connected routed    auto    auto    --
Vlan102       dev svi - DEMO PLE connected routed    auto    auto    --
Vlan103       test svi - DEMO PL connected routed    auto    auto    --
Vlan104       security svi - DEM connected routed    auto    auto    --
Vlan105       iot svi - DEMO PLE connected routed    auto    auto    --

!!!!!!! show cdp neighbors on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:19.516013

Capability Codes: R - Router, T - Trans-Bridge, B - Source-Route-Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater,
                  V - VoIP-Phone, D - Remotely-Managed-Device,
                  s - Supports-STP-Dispute

Device-ID          Local Intrfce  Hldtme Capability  Platform      Port ID

Total entries displayed: 0

!!!!!!! show int status on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:35.806752


--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
mgmt0         DO NOT TOUCH CONFI connected routed    full    1000    --         

--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
Eth1/1        --                 connected trunk     full    1000    10g        
Eth1/2        --                 connected trunk     full    1000    10g        
Eth1/3        --                 connected 1         full    auto    10g        
Eth1/4        --                 connected 1         full    auto    10g        
Eth1/5        L3 Link            connected routed    full    1000    10g        
< REDACTED FOR BREVITY>  
Po11          --                 connected trunk     full    1000    --         
Lo1           --                 connected routed    auto    auto    --         
Lo100         --                 connected routed    auto    auto    --         
Vlan1         --                 down      routed    auto    auto    --
Vlan100       mgmt svi - DEMO PL connected routed    auto    auto    --
Vlan101       prod svi - DEMO PL connected routed    auto    auto    --
Vlan102       dev svi - DEMO PLE connected routed    auto    auto    --
Vlan103       test svi - DEMO PL connected routed    auto    auto    --
Vlan104       security svi - DEM connected routed    auto    auto    --
Vlan105       iot svi - DEMO PLE connected routed    auto    auto    --

!!!!!!! show cdp neighbors on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:19.516013

Capability Codes: R - Router, T - Trans-Bridge, B - Source-Route-Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater,
                  V - VoIP-Phone, D - Remotely-Managed-Device,
                  s - Supports-STP-Dispute

Device-ID          Local Intrfce  Hldtme Capability  Platform      Port ID

Total entries displayed: 0

!!!!!!! show int status on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:35.806752


--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
mgmt0         DO NOT TOUCH CONFI connected routed    full    1000    --         

--------------------------------------------------------------------------------
Port          Name               Status    Vlan      Duplex  Speed   Type
--------------------------------------------------------------------------------
Eth1/1        --                 connected trunk     full    1000    10g        
Eth1/2        --                 connected trunk     full    1000    10g        
Eth1/3        --                 connected 1         full    auto    10g        
Eth1/4        --                 connected 1         full    auto    10g        
Eth1/5        L3 Link            connected routed    full    1000    10g        
< REDACTED FOR BREVITY>       
Po11          --                 connected trunk     full    1000    --         
Lo1           --                 connected routed    auto    auto    --         
Lo100         --                 connected routed    auto    auto    --         
Vlan1         --                 down      routed    auto    auto    --
Vlan100       mgmt svi - DEMO PL connected routed    auto    auto    --
Vlan101       prod svi - DEMO PL connected routed    auto    auto    --
Vlan102       dev svi - DEMO PLE connected routed    auto    auto    --
Vlan103       test svi - DEMO PL connected routed    auto    auto    --
Vlan104       security svi - DEM connected routed    auto    auto    --
Vlan105       iot svi - DEMO PLE connected routed    auto    auto    --

!!!!!!! show cdp neighbors on sbx-nxos-mgmt.cisco.com at 2019-09-12 22:36:36.812270

Capability Codes: R - Router, T - Trans-Bridge, B - Source-Route-Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater,
                  V - VoIP-Phone, D - Remotely-Managed-Device,
                  s - Supports-STP-Dispute

Device-ID          Local Intrfce  Hldtme Capability  Platform      Port ID

Total entries displayed: 0
```