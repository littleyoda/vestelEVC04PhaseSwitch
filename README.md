A simple script to change the number of phases used on an Vestel Home Plus EV04  wallbox.

The script does not(!) check whether a charging process is currently active.
The script should only be executed if no charging process is active. 

Query of the currently used phases

`python3 phaseswitch.py ip admin adminpwd`
 

Changing the phases in use to 3

`python3 phaseswitch.py ip admin adminpwd 3`

Changing the phases in use to 1

`python3 phaseswitch.py ip admin adminpwd 1`
