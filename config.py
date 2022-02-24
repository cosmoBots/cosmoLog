# Serial connection configuration
import os

cte_simulate_sensors = False
cte_emulate_devices = False

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

cfg_temp_read_period = 10.0
cfg_temp_nsamples_period1 = 60
cfg_temp_nsamples_period2 = 360

# cfg_press_read_period = 1.0  The period is already set in the Pfeiffer device
cfg_press_nsamples_period1 = 60
cfg_press_nsamples_period2 = 360

