# Serial connection configuration
import os

cte_simulate_sensors = False

if (os.name == 'nt'):
    if (cte_simulate_sensors):
        cte_serial_port = 'COM7:'   # Serial link port for windows machines
        cte_serial_port2 = 'COM7:'
    else:
        cte_serial_port = 'COM6:'   # Serial link port for windows machines
        cte_serial_port2 = 'COM5:'
else:
    cte_serial_port = '/dev/pfeiUSB'   # Serial link port for Linux machines    
    cte_serial_port2 = '/dev/lakeUSB'   # Serial link port for Linux machines

cte_verbose = True
