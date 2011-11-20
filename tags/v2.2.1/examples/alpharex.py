r'''Alpha Rex API

    A high-level, object-oriented programming interface to Lego MINDSTORMS
    NXT's "Alpha Rex" model (see [1] for assembling instructions), along with a
    small collection of functions demonstrating obvious usage scenarios.
    
    1. http://www.active-robots.com/products/mindstorms4schools/building-instructions.shtml
'''

from time import sleep

from nxt.brick import Brick
from nxt.locator import find_one_brick
from nxt.motor import Motor, PORT_A, PORT_B, PORT_C
from nxt.sensor import Light, Sound, Touch, Ultrasonic
from nxt.sensor import PORT_1, PORT_2, PORT_3, PORT_4


FORTH = 100
BACK = -100


class AlphaRex(object):
    r'''A high-level controller for the Alpha Rex model.
    
        This class implements methods for the most obvious actions performable
        by Alpha Rex, such as walk, wave its arms, and retrieve sensor samples.
        Additionally, it also allows direct access to the robot's components
        through public attributes.
    '''
    def __init__(self, brick='NXT'):
        r'''Creates a new Alpha Rex controller.
        
            brick
                Either an nxt.brick.Brick object, or an NXT brick's name as a
                string. If omitted, a Brick named 'NXT' is looked up.
        '''
        if isinstance(brick, basestring):
            brick = find_one_brick(name=brick)
    
        self.brick = brick
        self.arms = Motor(brick, PORT_A)
        self.legs = [Motor(brick, PORT_B), Motor(brick, PORT_C)]

        self.touch = Touch(brick, PORT_1)
        self.sound = Sound(brick, PORT_2)
        self.light = Light(brick, PORT_3)
        self.ultrasonic = Ultrasonic(brick, PORT_4)

    def echolocate(self):
        r'''Reads the Ultrasonic sensor's output.
        '''
        return self.ultrasonic.get_sample()
    
    def feel(self):
        r'''Reads the Touch sensor's output.
        '''
        return self.touch.get_sample()

    def hear(self):
        r'''Reads the Sound sensor's output.
        '''
        return self.sound.get_sample()

    def say(self, line, times=1):
        r'''Plays a sound file named (line + '.rso'), which is expected to be
            stored in the brick. The file is played (times) times.

            line
                The name of a sound file stored in the brick.

            times
                How many times the sound file will be played before this method
                returns.
        '''
        for i in range(0, times):
            self.brick.play_sound_file(False, line + '.rso')
            sleep(1)

    def see(self):
        r'''Reads the Light sensor's output.
        '''
        return self.light.get_sample()

    def walk(self, secs, power=FORTH):
        r'''Simultaneously activates the leg motors, causing Alpha Rex to walk.
        
            secs
                How long the motors will rotate.
            
            power
                The strength effected by the motors. Positive values will cause
                Alpha Rex to walk forward, while negative values will cause it
                to walk backwards. If you are unsure about how much force to
                apply, the special values FORTH and BACK provide reasonable
                defaults. If omitted, FORTH is used.
        '''
        for motor in self.legs:
            motor.run(power=power)
        
        sleep(secs)

        for motor in self.legs:
            motor.idle()

    def wave(self, secs, power=100):
        r'''Make Alpha Rex move its arms.
        
            secs
                How long the arms' motor will rotate.
            
            power
                The strength effected by the motor. If omitted, (100) is used.
        '''
        self.arms.run(power=power)
        sleep(secs)
        self.arms.idle()


def wave_and_talk():
    r'''Connects to a nearby Alpha Rex, then commands it to wave its arms and
        play the sound file 'Object.rso'.
    '''
    robot = AlphaRex()
    robot.wave(1)
    robot.say('Object')


def walk_forth_and_back():
    r'''Connects to a nearby Alpha Rex, then commands it to walk forward and
        then backwards.
    '''
    robot = AlphaRex()
    robot.walk(10, FORTH)
    robot.walk(10, BACK)


def walk_to_object():
    r'''Connects to a nearby Alpha Rex, then commands it to walk until it
        approaches an obstacle, then stop and say 'Object' three times.
    '''
    robot = AlphaRex()
    while robot.echolocate() > 10:
        robot.walk(1, FORTH)

    robot.say('Object', 3)


if __name__ == '__main__':
    walk_to_object()

