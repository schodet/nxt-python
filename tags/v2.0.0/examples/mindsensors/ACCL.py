### Examples of ACCL functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()    #find brick and connect
s = MSACCL(b, PORT_1)               #which sensor, brick and port
print s.get_offset('z')             #offset (xyz)
print s.get_range('x')              #range (xyz)
s.command(s.Commands.X_CALIBRATION) #See user guide or class def for more info
for i in range(10):
    print 'Tilt: ' + str(s.get_all_tilt())        #all tilt data
    print 'Tilt Y: ' + str(s.get_tilt('x'))     #x, y, or z get tilt data (works for accel too)
    print 'Accel: ' + str(s.get_sample())       #all accel data
    time.sleep(0.2)
b.sock.close()  #close bluetooth connection
