### Examples of LineLeader Functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import struct
import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSLineLeader(b, PORT_1)     #which sensor, brick and port

s.command(s.Commands.SENSOR_WAKE)          #sending commands
print s.get_steering()
print 'Result: ' + str(bin(s.get_result())) #to print result as byte
print 'Average: ' + str(s.get_average())    #Inserting text before values

for i in range(1, 9):
    print s.get_reading(i) #get_reading(1-8) in this case i will be 1-8
    time.sleep(.1)
print s.get_reading_all() #all sensors at the same time
b.sock.close()
