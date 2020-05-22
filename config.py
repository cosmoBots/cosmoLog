# Serial connection configuration
import os

if (os.name == 'nt'):
    cte_serial_port = 'COM6:'   # Serial link port for windows machines
    cte_serial_port2 = 'COM5:'
else:
    cte_serial_port = '/dev/pfeiUSB'   # Serial link port for Linux machines    
    cte_serial_port2 = '/dev/lakeUSB'   # Serial link port for Linux machines

cte_verbose = True
