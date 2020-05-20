# ['Common imports' begin (DON'T REMOVE THIS LINE!)]
from PfLog2_CI import *
# ['Common imports' end (DON'T REMOVE THIS LINE!)]

# ['Common definitions for 'Hierarchical State Chart generator'' begin (DON'T REMOVE THIS LINE!)]
# Code items' definitions
def serialCharRead(  ):
    # ['<global>::serialCharRead' begin]
    dre2.byte_read = dre2.ser.read(1)

    dre2.char_read = dre2.byte_read.decode('ascii')[0]

    dre2.int_read = int.from_bytes(dre2.byte_read, byteorder='big')
    # ['<global>::serialCharRead' end]

# ['Common definitions for 'Hierarchical State Chart generator'' end (DON'T REMOVE THIS LINE!)]

# ['sendCtrlCommand' begin (DON'T REMOVE THIS LINE!)]
# State IDs
ID_SENDCTRLCOMMAND_INITIAL = 0
ID_SENDCTRLCOMMAND_FINAL = 1

def sendCtrlCommand(  ):
    # set initial state
    state = ID_SENDCTRLCOMMAND_INITIAL

    while( True ):
        # State ID: ID_SENDCTRLCOMMAND_INITIAL
        if( state==ID_SENDCTRLCOMMAND_INITIAL ):
            # Transition ID: ID_SENDCTRLCOMMAND_TRANSITION_CONNECTION
            # Actions:
            # ['<global>::serialCommandWrite' begin]
            dre2.ser.write(dre2.command_tx_buf+chr(13))
            # ['<global>::serialCommandWrite' end]
            state = ID_SENDCTRLCOMMAND_FINAL

        # State ID: ID_SENDCTRLCOMMAND_FINAL
        elif( state==ID_SENDCTRLCOMMAND_FINAL ):
            return ID_SENDCTRLCOMMAND_FINAL

# ['sendCtrlCommand' end (DON'T REMOVE THIS LINE!)]

# ['getCtrlResponse' begin (DON'T REMOVE THIS LINE!)]
# State IDs
ID_GETCTRLRESPONSE_INITIAL = 2
ID_GETCTRLRESPONSE_FINAL = 3
ID_GETCTRLRESPONSE_READING = 4
ID_GETCTRLRESPONSE_FINISHING = 5

def getCtrlResponse(  ):
    # set initial state
    state = ID_GETCTRLRESPONSE_INITIAL

    while( True ):
        # State ID: ID_GETCTRLRESPONSE_INITIAL
        if( state==ID_GETCTRLRESPONSE_INITIAL ):
            # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
            # Actions:
            # ['<global>::resetRxTask' begin]
            dre2.command_rx_buf = []
            dr2e.command_rx_str = ""
            # ['<global>::resetRxTask' end]
            serialCharRead()
            state = ID_GETCTRLRESPONSE_READING

        # State ID: ID_GETCTRLRESPONSE_READING
        elif( state==ID_GETCTRLRESPONSE_READING ):
            if( dr2e.char_read==chr(10) or dr2e.char_read==chr(13) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                serialCharRead()
                state = ID_GETCTRLRESPONSE_FINISHING

            elif( (dr2e.char_read != chr(10)) and (dr2e.char_read != chr(13)) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                # ['<global>::appendCharToRxBuf' begin]
                dr2e.command_rx_buf.append(dr2e.int_read)
                d2re.command_rx_str += d2re.char_read
                # ['<global>::appendCharToRxBuf' end]
                serialCharRead()

        # State ID: ID_GETCTRLRESPONSE_FINISHING
        elif( state==ID_GETCTRLRESPONSE_FINISHING ):
            if( d2re.char_read==chr(10) or d2re.char_read==chr(13) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                state = ID_GETCTRLRESPONSE_FINAL

            elif( (d2re.char_read != chr(10)) and (d2re.char_read != chr(13)) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                serialCharRead()

        # State ID: ID_GETCTRLRESPONSE_FINAL
        elif( state==ID_GETCTRLRESPONSE_FINAL ):
            return ID_GETCTRLRESPONSE_FINAL

# ['getCtrlResponse' end (DON'T REMOVE THIS LINE!)]
