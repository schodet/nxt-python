# Examples of HID Functions
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list
# Types 'Hello World!' into selected area and then selects all text

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSHID(b, PORT_1)  

s.command(s.Commands.ASCII_MODE)  #Set to ASCii mode
s.write_data('H')
s.command(s.Commands.TRANSMIT)  #Transmit data to usb host
s.write_data('E')
s.command(s.Commands.TRANSMIT)
s.write_data('L')
s.command(s.Commands.TRANSMIT)
s.write_data('L')
s.command(s.Commands.TRANSMIT)
s.write_data('O')
s.command(s.Commands.TRANSMIT)
s.write_data(' ')
s.command(s.Commands.TRANSMIT)
s.write_data('W')
s.command(s.Commands.TRANSMIT)
s.write_data('O')
s.command(s.Commands.TRANSMIT)
s.write_data('R')
s.command(s.Commands.TRANSMIT)
s.write_data('L')
s.command(s.Commands.TRANSMIT)
s.write_data('D')
s.command(s.Commands.TRANSMIT)
s.write_data('!')
s.command(s.Commands.TRANSMIT)

s.command(s.Commands.DIRECT_MODE)  #Direct data mode
s.set_modifier(0x01)
s.command(s.Commands.ASCII_MODE)
s.write_data('a')
s.command(s.Commands.TRANSMIT)
b.sock.close()
