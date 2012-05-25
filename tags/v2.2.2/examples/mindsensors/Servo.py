### Example of Servo Functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSServo(b, PORT_1)          #which sensor, brick and port to talk to
s.set_speed(1, 0)   #how to set speed. (motor#, speed value)
s.set_quick(3, 150) #quick position registers(motor# 1-8, position value 50-250)
s.command('I3') #sending commands
                #more explanation in user guides, www.mindsensors.com

for i in range (3):
    s.set_quick(1, 150)     
    time.sleep(.5)      #wait .5 seconds
    s.set_position(1, 1700) #move to position (Motor#, position value 500-2500)

b.sock.close()          #close bluetooth connection
