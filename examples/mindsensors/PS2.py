### Examples of PS2 functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSPS2(b, PORT_1)           #which sensor, brick and port
s.command(s.Commands.POWER_ON)
previous_buttons = 0
for i in range(15):
    time.sleep(.2)
    print 'left X: ' + str(s.get_joystick('x', 'left'))
    time.sleep(.2)
    print 'right Y: ' + str(s.get_joystick('y', 'right'))
    time.sleep(.2)
    buttons = s.get_buttons(1)
    if buttons != previous_buttons:
        print buttons
        previous_buttons = buttons
b.sock.close()


