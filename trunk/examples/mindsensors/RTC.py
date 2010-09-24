### Example RTC functions ###
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSRTC(b, PORT_1)           #which sensor, brick and port


print 'Today is: ' + str(s.get_month()) + \
'/' + str(s.get_date()) + '/' + str(s.get_year()) 

print 'day of week: ' + str(s.get_day())

s.hour_mode(12) #set to 12-hour mode
t = 'Time of day (12hr): ' + str(s.get_hours()) + \
':' + str(s.get_minutes()) 

m = s.get_mer() #get AM/PM
if m == 0:
    m = 'am'
elif m == 1:
    m = 'pm'
    
print str(t) + str(m)

s.hour_mode(24) #set to 24-hour mode
t = 'Time of day (24hr): ' + str(s.get_hours()) + \
':' + str(s.get_minutes()) 
print t

for i in range(20):
    print s.get_seconds()
    time.sleep(1)
b.sock.close()
