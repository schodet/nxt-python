# NXT-MMX Function examples
### User guide at http://www.mindsensors.com/index.php?module=documents&JAS_DocumentManager_op=list

import nxt.locator, time
from nxt.sensor import *
b = nxt.locator.find_one_brick()#find brick and connect
s = MSMMX(b, PORT_1)
s.command('R')

print s.get_encoder_pos(1)      #get encoder position(Motor#)
print s.read_value('command_a_1')[0] #Read values in command register a
for i in range(8):
    s.command_a(1, i, 1)    #write to motor command register 
    #(motor#, bit#, bitvalue)
    s.command_a(2, i , 1)
    time.sleep(.1)
s.set_speed(1, 100)     #set speed
s.set_time_run(1, 5)    #Time to run (Motor#, time in seconds)
s.set_speed(2, 100)
s.set_time_run(2, 5)   
s.command_a(1, 7, 1) #Tell motors to GO!
s.command_a(2, 7, 1)
time.sleep(.1)
print s.get_tasks(1)      # motor tasks running
print s.get_motor_status(1, 7)
time.sleep(6)
s.set_encoder_target(1, 1000)
s.set_encoder_target(2, 500)
for i in range(1,3): #GO
    s.command_a(i, 7, 1)

s.set_tolerance(80)     #set encoder positioning tolerance
s.set_pass_count(5)     #Higher number = more time, but more acuracy positioning
s.set_pid('p', 'speed', 50) #example values, these may cause motors to not run
s.set_pid('d', 'encoder', 10)   #if so unplug from power source
b.sock.close()
