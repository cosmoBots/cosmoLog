# Serial connection configuration
import os

if (os.name == 'nt'):
    cte_serial_port = 'COM6:'   # Serial link port for windows machines
else:
    cte_serial_port = '/dev/ttyUSB0'   # Serial link port for Linux machines


cte_verbose = True