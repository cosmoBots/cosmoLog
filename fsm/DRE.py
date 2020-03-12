class DRE:
    command_rx_buf = bytearray(128)
    command_rx_str = ""
    char_read = ''
    byte_read = 0
    int_read = 0
    ser = None
