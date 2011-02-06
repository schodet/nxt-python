### Examples of all MTRMUX functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSMTRMUX(b, PORT_1) #0xB4
for i in range(3):
    s.set_speed(1, 200)     # (Motor#, speed value 0-255)
    s.set_direction(1, 1)   # (Motor#, direction 0-1)
    s.set_speed(2, 250)     # (Motor#, speed value 0-255)
    s.set_direction(2, 1)
    s.set_speed(3, 200)     # (Motor#, speed value 0-255)
    s.set_direction(3, 1)
    s.set_speed(4, 200)     # (Motor#, speed value 0-255)
    s.set_direction(4, 1)
    time.sleep(1)       # pause

    s.command(s.Commands.BRAKE)  #send commands below
    s.set_direction(1, 2)
    s.set_speed(1, 200)     
    s.set_direction(1, 2)  
    s.set_speed(2, 250)    
    s.set_direction(2, 2)
    s.set_speed(3, 200)    
    s.set_direction(3, 2)
    s.set_speed(4, 200)    
    s.set_direction(4, 2)
    s.command(s.Commands.FLOAT)
    
b.sock.close()
