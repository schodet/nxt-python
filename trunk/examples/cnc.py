#Script to control a NXT 2-axis CNC "Pancake maker"
#Illustrates controlling more than one motor at the same time without trying to
#sync them. Uses the thread module.
#Written 2/3/11 by Marcus Wanner
#
#For more info and warnings see:
#http://groups.google.com/group/nxt-python/browse_thread/thread/f6ef0865ae768ef

import nxt, thread, time
b = nxt.find_one_brick()
mx = nxt.Motor(b, nxt.PORT_A)
my = nxt.Motor(b, nxt.PORT_B)
motors = [mx, my]

def turnmotor(m, power, degrees):
	m.turn(power, degrees)

#here are the instructions...
#the first value is the time to start the instruction
#the second is the axis (0 for x, 1 for y)
#the third is the power
#the fourth is the degrees
#it's probably not a good idea to run simultaneous turn
#functions on a single motor, so be careful with this
instructions = (
	[0, 0, 80, 180],
	[0, 1, -40, 1080],
	[1, 0, -80, 180],
	[2, 0, 80, 180],
	[3, 1, 100, 360],
	[3, 0, -100, 360],
)
#how long from start until the last instruction is ended
length = 5

def runinstruction(i):
	motorid, speed, degrees = i
	#THIS IS THE IMPORTANT PART!
	thread.start_new_thread(
		turnmotor,
		(motors[motorid], speed, degrees))

#main loop
seconds = 0
while 1:
	print "Tick %d" % seconds
	for i in instructions:
		if i[0] == seconds:
			runinstruction(i[1:])
	seconds = seconds + 1
	if seconds >= length:
		break
	time.sleep(1)
