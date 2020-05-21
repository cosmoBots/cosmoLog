# ['Common imports' begin (DON'T REMOVE THIS LINE!)]
from PfLog_CI import *
# ['Common imports' end (DON'T REMOVE THIS LINE!)]

# ['Common definitions for 'Hierarchical State Chart generator'' begin (DON'T REMOVE THIS LINE!)]
# Code items' definitions
def serialCharRead(  ):
    # ['<global>::serialCharRead' begin]
    dre.byte_read = dre.ser.read(1)

    dre.char_read = dre.byte_read.decode('ascii')[0]

    dre.int_read = int.from_bytes(dre.byte_read, byteorder='big')
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
            dre.ser.write(dre.command_tx_buf+chr(13).encode()+chr(10).encode())
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
            dre.command_rx_buf = []
            dre.command_rx_str = ""
            # ['<global>::resetRxTask' end]
            serialCharRead()
            state = ID_GETCTRLRESPONSE_READING

        # State ID: ID_GETCTRLRESPONSE_READING
        elif( state==ID_GETCTRLRESPONSE_READING ):
            if( dre.char_read==chr(10) or dre.char_read==chr(13) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                serialCharRead()
                state = ID_GETCTRLRESPONSE_FINISHING

            elif( (dre.char_read != chr(10)) and (dre.char_read != chr(13)) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                # ['<global>::appendCharToRxBuf' begin]
                dre.command_rx_buf.append(dre.int_read)
                dre.command_rx_str += dre.char_read
                # ['<global>::appendCharToRxBuf' end]
                serialCharRead()

        # State ID: ID_GETCTRLRESPONSE_FINISHING
        elif( state==ID_GETCTRLRESPONSE_FINISHING ):
            if( dre.char_read==chr(10) or dre.char_read==chr(13) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                state = ID_GETCTRLRESPONSE_FINAL

            elif( (dre.char_read != chr(10)) and (dre.char_read != chr(13)) ):
                # Transition ID: ID_GETCTRLRESPONSE_TRANSITION_CONNECTION
                # Actions:
                serialCharRead()

        # State ID: ID_GETCTRLRESPONSE_FINAL
        elif( state==ID_GETCTRLRESPONSE_FINAL ):
            return ID_GETCTRLRESPONSE_FINAL

# ['getCtrlResponse' end (DON'T REMOVE THIS LINE!)]
