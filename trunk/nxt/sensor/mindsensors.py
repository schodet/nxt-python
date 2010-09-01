# nxt.sensor.mindsensors module -- Classes implementing Mindsensors sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  Marcus Wanner, MindSensors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


from .common import *
from .digital import BaseDigitalSensor, SensorInfo
from .analog import BaseAnalogSensor

class Sensor_Info:
    def Version(self):
        return self.read_value(0x00, str)

    def Vendor(self):
        return self.read_value(0x80, str)


class SumoEyesReading:
    """Contains the reading of SumoEyes sensor. left and right can be True or
    False. If True, then there is something there, if False, then it's empty
    there.
    """
    def __init__(self, raw_reading):
        self.raw = raw_reading
        val = raw_reading.normalized_ad_value # FIXME: make it rely on raw_ad_value
        right = 600 < val < 700
        both = 700 <= val < 900
        left = 300 < val < 400
        self.left = left or both
        self.right = right or both
    
    def __str__(self):
        return '(left: ' + str(self.left) + ', right: ' + str(self.right) + ')'

class SumoEyes(BaseAnalogSensor):   
    """The class to control Mindsensors Sumo sensor. Warning: long range not
    working for my sensor.
    """
    #range: 5-10cm
    def __init__(self, brick, port, long_range=False):
        super(SumoEyes, self).__init__(brick, port)
        self.set_long_range(long_range)
        
    def set_long_range(self, val):
        """Sets if the sensor should operate in long range mode (12 inches) or
        the short range mode (6 in). val should be True or False.
        """
        if val:
            type_ = Type.LIGHT_INACTIVE
        else:
            type_ = Type.LIGHT_ACTIVE
        self.set_input_mode(type_, Mode.RAW)
    
    def get_sample(self):
        """Returns the processed meaningful values of the sensor"""
        return SumoEyesReading(self.get_input_values())


class CompassCommand:
    'Namespace for enumeration compass sensor commands'
    # NOTE: just a namespace (enumeration)
    AUTO_TRIG_ON = (0x41, 0x02)
    AUTO_TRIG_OFF = (0x53, 0x01)
    MAP_HEADING_BYTE = 0x42        # map heading to 0-255 range
    MAP_HEADING_INTEGER = 0x49    # map heading to 0-36000 range
    SAMPLING_50_HZ = 0x45        # set sampling frequency to 50 Hz
    SAMPLING_60_HZ = 0x55        # set sampling frequency to 60 Hz
    SET_ADPA_MODE_ON = 0x4E        # set ADPA mode on
    SET_ADPA_MODE_OFF = 0x4F    # set ADPA mode off
    BEGIN_CALIBRATION = 0x43    # begin calibration
    DONE_CALIBRATION = 0x44        # done with calibration
    LOAD_USER_CALIBRATION = 0x4C    # load user calibration value

class Compass(BaseDigitalSensor):   
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command': (0x41, '<B'),
                        'heading': (0x42, '<H'),
                        'x_offset': (0x44, '<H'),
                        'y_offset': (0x46, '<H'),
                        'x_range': (0x48, '<H'),
                        'y_range': (0x4A, '<H'),
                        'x_raw': (0x4C, '<H'),
                        'y_raw': (0x4E, '<H'),
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(Compass, self).__init__(brick, port, check_compatible)
        self.write_value('command', (CompassCommand.MAP_HEADING_INTEGER, )) # is this necessary?

    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))
    
    def get_heading(self):
        return self.read_value('heading')[0]
        
    get_sample = get_heading

Compass.add_compatible_sensor(None, 'mndsnsrs', 'CMPS')


class DistCommand:
    TYPE_GP2D12 = 0x31 #GP2D12 sensor Module
    TYPE_GP2D120 = 0x32 #Short range sensor Module
    TYPE_GP2Y0A21YK = 0x33 #Medium range sensor Module
    TYPE_GP2Y0A02YK = 0x34 #Long range sensor Module
    TYPE_CUSTOM = 0x35 #Custom sensor Module
    POWER_ON = 0x45 #Sensor module power on
    POWER_OFF = 0x44 #Sensor module power offset
    ADPA_ON = 0x4E #ADPA mode on
    ADPA_OFF = 0x4F #ADPA mode off (default)

class DIST(BaseDigitalSensor):  
    """Class for the Distance Infrared Sensor"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command': (0x41, '<B'),
                        'distance': (0x42, '<H'),
                        'voltage': (0x44, '<H'),
                        'type': (0x50, '<B'),
                        'no_of_data_points': (0x51, '<B'),
                        'min_distance': (0x52, '<H'),
                        'max_distance': (0x54, '<H'),
    })
    
    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))
    
    def get_distance(self):
        return self.read_value('distance')[0]

    get_sample = get_distance

    def get_type(self):
        return self.read_value('type')[0]
        
    def get_voltage(self):
        return self.read_value('voltage')[0]
    
    def get_min_distance(self):
        return self.read_value('min_distance')[0]
        
    def get_max_distance(self):
        return self.read_value('max_distance')[0]

DIST.add_compatible_sensor(None, 'mndsnsrs', 'DIST')


class RTC(BaseDigitalSensor):
    """Class for the RealTime Clock sensor"""
    #   has no sensor indentification or commands
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'seconds': (0x00, '<B'),
                        'minutes': (0x01, '<B'),
                        'hours':   (0x02, '<B'),
                        'day':     (0x03, '<B'),
                        'date':    (0x04, '<B'),
                        'month':   (0x05, '<B'),
                        'year':    (0x06, '<B'),
                      })
    I2C_DEV = 0xD0

    def __init__(self, brick, port, check_compatible=False): #check_compatible must remain false due to no identification!
        super(RTC, self).__init__(brick, port, check_compatible)

    def get_seconds(self):  
        gs = self.read_value('seconds')[0]
        gs2 = gs & 0xf  # bitmasks
        gs3 = gs & 0x70
        gs3 = gs3 >> 4
        return str(gs3) + str(gs2)
    
    def get_minutes(self):
        gm = self.read_value('minutes')[0]
        gm2 = gm & 0xf
        gm3 = gm & 0x70
        gm3 = gm3 >> 4
        return str(gm3) + str(gm2)
        
    def get_hours(self):    
        gh = self.read_value('hours')[0]
        gh2 = gh & 0xf
        gh3 = gh & 0x30
        gh3 = gh3 >> 4
        return str(gh3) + str(gh2)

    def get_day(self):      
        gwd = self.read_value('day')[0]
        gwd = gwd & 0x07
        return gwd

    def get_month(self):    
        gmo = self.read_value('month')[0]
        gmo2 = gmo & 0xf
        gmo3 = gmo & 0x10
        gmo3 = gmo3 >> 4
        return str(gmo3) + str(gmo2)

    def get_year(self):
        """Last two digits (10 for 2010)"""
        gy = self.read_value('year')[0]
        gy2 = gy & 0xf
        gy3 = gy & 0xF0
        gy3 =  gy3 >> 4
        return str(gy3) + str(gy2)

    def get_date(self):
        gd = self.read_value('date')[0]
        gd2 = gd & 0xf
        gd3 = gd & 0x60
        gd3 = gd3 >> 4
        return str(gd3) + str(gd2)

    def hour_mode(self, mode):
        """Writes mode bit and re-enters hours, which is required"""
        if mode == 12 or 24:
            hm = self.read_value('hours')[0]
            hm2 = hm & 0x40
            hm2 = hm2 >> 6
            if mode == 12 and hm2 == 0:  #12_HOUR = 1
                hm3 = hm + 64
                self.write_value('hours', (hm3, ))
            elif mode == 24 and hm2 == 1:  #24_HOUR = 0
                hm3 = hm - 64
                self.write_value('hours', (hm3, ))
            else:
                print 'That mode is already selected!'
        else:
            raise ValueError('Must be 12 or 24!')

    def get_mer(self):
        mer = self.read_value('hours')[0]
        mer2 = mer & 0x40
        mer2 = mer2 >> 6
        if mer2 == 1:
            mer3 = mer & 0x20
            mer3 = mer3 >> 0x10
            return mer3
        else:
            print 'Cannot get mer! In 24-hour mode!'


class AcclCommand:
    X_CALIBRATION = 'X' #Acquire X point calibration
    X_CAL_AND_END = 'x' #X point calibration and end calibration
    Y_CALIBRATION = 'Y' #Acquire Y point calibration
    Y_CAL_AND_END = 'y' #Y point calibration and end calibration
    Z_CALIBRATION = 'Z' #Acquire Z point calibration
    Z_CAL_AND_END = 'z' #Z point calibration and end calibration
    CAL_RESET = 'R' #Reset to factory set calibration
    ADPA_ON = 'N' #Set ADPA mode On
    ADPA_OFF = 'O' #Set ADPA mode Off (default)

class ACCL(BaseDigitalSensor):
    """Class for Accelerometer sensor"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command':      (0x41, '<B'),
                        'x_tilt':       (0x42, '<B'),
                        'y_tilt':       (0x43, '<B'),
                        'z_tilt':       (0x44, '<B'),

                        'x_accel_LSB':   (0x45, '<H'),
                        'x_accel_msb':   (0x46, '<B'),

                        'y_accel_LSB':  (0x47, '<H'),
                        'y_accel_MSB':  (0x48, '<B'),

                        'z_accel_LSB':  (0x49, '<H'),
                        'z_accel_MSB':  (0x4A, '<B'),

                        'x_offset_LSB': (0x4B, '<H'),
                        'x_offset_MSB': (0x4C, '<B'),
                        'x_range_LSB':  (0x4D, '<H'),
                        'x_range_MSB':  (0x4E, '<B'),

                        'y_offset_LSB': (0x4F, '<H'),
                        'y_offset_MSB': (0x50, '<B'),
                        'y_range_LSB':  (0x51, '<H'),
                        'y_range_MSB':  (0x52, '<B'),

                        'z_offset_LSB': (0x53, '<H'),
                        'z_offset_MSB': (0x54, '<B'),
                        'z_range_LSB':  (0x55, '<H'),
                        'z_range_MSB':  (0x56, '<B'),
                      })

    def __init__(self, brick, port, check_compatible=False):
        super(ACCL, self).__init__(brick, port, check_compatible)

    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))

    def get_tilt(self, letter):
        xyz = str(letter) + '_tilt'
        return self.read_value(xyz)[0]
    
    def get_accel(self, letter):
        xyz = str(letter) + '_accel_LSB'
        return self.read_value(xyz)[0]

    def offset(self, letter, value):
        xyz = str(letter) + '_offset_LSB'
        self.write_value(xyz, (value, ))

    def set_range(self, letter, value):
        xyz = str(letter) + '_range_LSB'
        self.write_value(xyz, (value, ))

ACCL.add_compatible_sensor(None, 'mndsnsrs', 'ACCL-NX') #Tested with version 'V3.20'


class MtrmuxCommand:
    FLOAT = 0x00
    FORWARD = 0x01
    REVERSE = 0x02
    BRAKE = 0x03
    
class MTRMUX(BaseDigitalSensor):
    """Class for Motor Multiplexer sensor"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command'     :  (0x41, '<B'),
                        'direction_m1':  (0x42, '<B'),
                        'speed_m1':      (0x43, '<B'),
                        'direction_m2':  (0x44, '<B'),
                        'speed_m2':      (0x45, '<B'),
                        'direction_m3':  (0x46, '<B'),
                        'speed_m3':      (0x47, '<B'),
                        'direction_m4':  (0x48, '<B'),
                        'speed_m4':      (0x49, '<B'),
                      })
    I2C_DEV = 0xB4
    
    def __init__(self, brick, port, check_compatible=False):
        super(MTRMUX, self).__init__(brick, port, check_compatible)

    def command(self, command):
        self.write_value('command', (command, )) 

    def direction(self, number, value):
        addressname = 'direction_m' + str(number)
        self.write_value(addressname, (value, ))

    def speed(self, number, value):
        addressname = 'speed_m' + str(number)
        self.write_value(addressname, (value, ))
            
MTRMUX.add_compatible_sensor(None, 'mndsnsrs', 'MTRMUX') #Tested with version 'V2.11'


class LineLeaderCommand:
    CALIBRATE_WHITE = 'W'
    CALIBRATE_BLACK = 'B'
    SENSOR_SLEEP = 'D'
    US_CONFIG = 'A'
    EU_CONFIG = 'E'
    UNI_CONFIG = 'U'
    SENSOR_WAKE = 'P'
    COLOR_INVERT = 'I'
    COLOR_INVERT_REVERSE = 'R'
    SNAPSHOT = 'S'

class LineLeader(BaseDigitalSensor):
    """Class for Line Sensor Array"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command':   (0x41, '<B'),
                        'steering':  (0x42, '<B'),
                        'average':   (0x43, '<B'),
                        'result':    (0x44, '<B'),
                        'set_point': (0x45, '<B'),
                
                        'kp':        (0x46, '<B'),
                        'ki':        (0x47, '<B'),
                        'kd':        (0x48, '<B'),
                        'kp_divisor':(0x61, '<B'),
                        'ki_divisor':(0x62, '<B'),
                        'kd_divisor':(0x63, '<B'),
                 #One byte for each sensor, so byte# = sensor#
                        'calibrated_reading_byte1':  (0x49, '<B'),
                        'calibrated_reading_byte2':  (0x4A, '<B'),
                        'calibrated_reading_byte3':  (0x4B, '<B'),
                        'calibrated_reading_byte4':  (0x4C, '<B'),
                        'calibrated_reading_byte5':  (0x4D, '<B'),
                        'calibrated_reading_byte6':  (0x4E, '<B'),
                        'calibrated_reading_byte7':  (0x4F, '<B'),
                        'calibrated_reading_byte8':  (0x50, '<B'),

                        'w_read_limit':(0x51, '<H'),
                        'b_read_limit':(0x59, '<B'),
                        'w_cal_data1':(0x64, '<B'),
                        'b_cal_data':(0x6C, '<B'),

                        'uncal_sensor1_voltage_byte1':(0x74, '<B'),
                        'uncal_sensor2_voltage_byte1':(0x76, '<B'),
                        'uncal_sensor3_voltage_byte1':(0x78, '<B'),
                        'uncal_sensor4_voltage_byte1':(0x7A, '<B'),
                        'uncal_sensor5_voltage_byte1':(0x7C, '<B'),
                        'uncal_sensor6_voltage_byte1':(0x7E, '<B'),
                        'uncal_sensor7_voltage_byte1':(0x80, '<B'),
                        'uncal_sensor8_voltage_byte1':(0x82, '<B'),
                      })
    
    def __init__(self, brick, port, check_compatible=False):
        super(LineLeader, self).__init__(brick, port, check_compatible)

    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))

    def get_steering(self):
        return self.read_value('steering')[0]

    def get_average(self):
        return self.read_value('average')[0]

    def get_result(self):
        return self.read_value('result')[0]

    def set_point(self, value):
        self.write_value('set_point', (value, ))

    def pid(self, pid, value):
        addressname = 'k' + str(pid)
        self.write_value(addressname, (value, ))

    def pid_divisor(self, pid, value):
        addressname = 'k' + str(pid) +  '_divisor'
        self.write_value(addressname, (value, ))

    def get_reading(self, number):
        addressname = 'calibrated_reading_byte' + str(number)
        return self.read_value(addressname)[0]

LineLeader.add_compatible_sensor(None, 'mndsnsrs', 'LineLdr') #Tested with version 'V1.16'


class ServoCommand:
    RESUME_MACRO = 'R'
    RESET_POS_SPEED = 'S'
    STORE_MOTOR_POS_1 = 'I1'
    STORE_MOTOR_POS_2 = 'I2'
    STORE_MOTOR_POS_3 = 'I3'
    STORE_MOTOR_POS_4 = 'I4'
    STORE_MOTOR_POS_5 = 'I5'
    STORE_MOTOR_POS_6 = 'I6'
    STORE_MOTOR_POS_7 = 'I7'
    STORE_MOTOR_POS_8 = 'I8'
    HALT_MACRO = 'H'
    X_TO_VAR = 'Gx' #not going to work yet
    EDIT_MACRO = 'EM'
    PAUSE_MACRO = 'P'

class Servo(BaseDigitalSensor):
    """Class for Servo sensors"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command'  : (0x41, '<B'),

                        'servo_1_pos':  (0x42, '<H'),
                        'servo_2_pos':  (0x44, '<H'),
                        'servo_3_pos':  (0x46, '<H'),
                        'servo_4_pos':  (0x48, '<H'),
                        'servo_5_pos':  (0x4A, '<H'),
                        'servo_6_pos':  (0x4C, '<H'),
                        'servo_7_pos':  (0x4E, '<H'),
                        'servo_8_pos':  (0x50, '<H'),

                        'servo_1_speed':    (0x52, '<B'),
                        'servo_2_speed':    (0x53, '<B'),
                        'servo_3_speed':    (0x54, '<B'),
                        'servo_4_speed':    (0x55, '<B'),
                        'servo_5_speed':    (0x56, '<B'),
                        'servo_6_speed':    (0x57, '<B'),
                        'servo_7_speed':    (0x58, '<B'),
                        'servo_8_speed':    (0x59, '<B'),
                  
                        'servo_1_quick':      (0x5A, '<H'),
                        'servo_2_quick':      (0x5B, '<H'),
                        'servo_3_quick':      (0x5C, '<H'),
                        'servo_4_quick':      (0x5D, '<H'),
                        'servo_5_quick':      (0x5E, '<H'),
                        'servo_6_quick':      (0x5F, '<H'),
                        'servo_7_quick':      (0x60, '<H'),
                        'servo_8_quick':      (0x61, '<H'),
                     })
    I2C_DEV = 0xB0

    COMMANDVALUES = {'R':  (0x52),   #Resume macro execution
                'S':  (0x53),   #reset initial position and speed
                'I1': (0x4931), #store initial position motor 1
                'I2': (0x4932), #store initial position motor 2
                'I3': (0x4933), #etc...
                'I4': (0x4934),
                'I5': (0x4935),
                'I6': (0x4936),
                'I7': (0x4937),
                'I8': (0x4938),
                'H':  (0x48),   #Halt macro
                'Gx': (0x4778), #not going to work yet x = variable
                'EM': (0x454d), #Edit Macro
                'P':  (0x50),   #Pause Macro
                }

    def __init__(self, brick, port, check_compatible=False):
        super(Servo, self).__init__(brick, port, check_compatible)
        
    def command(self, command):
        value = self.COMMANDVALUES[command]
        self.write_value('command', (value, ))

    def position(self, number, value):
       addressname = 'servo_' + str(number) + '_pos'
       self.write_value(addressname, (value, ))

    def speed(self, number, value):
       addressname = 'servo_' + str(number) + '_pos'
       self.write_value(addressname, (value, ))
       
    def quick(self, number, value):
           addressname = 'servo_' + str(number) + '_pos'
           self.write_value(addressname, (value, ))
            
Servo.add_compatible_sensor(None, 'mndsnsrs', 'NXTServo') #Tested with version 'V1.20'


class MmxCommand:
    RESET_PARAMS_ENCODERS = 'R'
    ISSUE_SYNCED_COMMANDS = 'S'
    MOTOR_1_FLOAT_STOP = 'a'
    MOTOR_2_FLOAT_STOP = 'b'
    BOTH_FLOAT_STOP = 'c'
    MOTOR_1_BRAKE_STOP = 'A'
    MOTOR_2_BRAKE_STOP = 'B'
    BOTH_BRAKE_STOP = 'C'
    MOTOR_1_ENC_RESET = 'r'
    MOTOR_2_ENC_RESET = 's'

class MMX(BaseDigitalSensor):
    """Class for MMX sensors"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command'  :        (0x41, '<B'),
                        #Motor Writes
                        'encoder_1_target': (0x42, '<H'),
                        'speed_1':          (0x46, '<B'),
                        'seconds_to_run_1': (0x47, '<B'),
                        'command_b_1':      (0x48, '<B'),
                        'command_a_1':      (0x49, '<B'),

                        'encoder_2_target': (0x4A, '<H'),
                        'speed_2':          (0x4E, '<B'),
                        'seconds_to_run_2': (0x4F, '<B'),
                        'command_b_2':      (0x50, '<B'),
                        'command_a_2':      (0x51, '<B'),
                        #Motor reads
                        'encoder_1_pos':    (0x62, '<H'),
                        'encoder_2_pos':    (0x66, '<H'),
                        'status_m1':        (0x72, '<B'),
                        'status_m2':        (0x73, '<B'),
                        'tasks_running_m1': (0x76, '<H'),
                        'tasks_running_m2': (0x77, '<H'),
                        #PID Control
                        'p_encoder':       (0x7A, '<H'),
                        'i_encoder':       (0x7C, '<H'),
                        'd_encoder':       (0x7E, '<H'),
                        'p_speed':         (0x80, '<H'),
                        'i_speed':         (0x82, '<H'),
                        'd_speed':         (0x84, '<H'),
                        'pass_count':       (0x86, '<B'),
                        'tolerance':        (0x87, '<B'),
                  })      
    I2C_DEV = 0x06
    
    def __init__(self, brick, port, check_compatible=False):
        super(MMX, self).__init__(brick, port, check_compatible)
    
    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))

    def encoder_target(self, motor_number, value):
        addressname = 'encoder_' + str(motor_number) + '_target'
        self.write_value(addressname, (value, ))

    def speed(self, motor_number, value):
        addressname = 'speed_' + str(motor_number)
        self.write_value(addressname, (value, ))

    def time_run(self, motor_number, seconds):
        addressname = 'seconds_to_run_' + str(motor_number)
        self.write_value(addressname, (seconds, ))

    def command_b(self, motor_number, value):
        addressname = 'command_b_' + str(motor_number)
        self.write_value(addressname, (value, ))

    def command_a(self, motor_number, bit_num, bit_val):
        addressname = 'command_a_' + str(motor_number)
        s = self.read_value(addressname)[0]
        #I feel like there must be an easier way to write one bit...
        val = bit_val << bit_num
        if bit_val == 1:    
            value = val | s
            self.write_value(addressname, (value, ))
            return value #testing purposes
        elif bit_val == 0:
            val = 1
            val = val << bit_num
            val = val ^ 0xFF
            value = val & s
            self.write_value(addressname, (value, ))
            return value
            
    def encoder_pos(self, motor_number):
        addressname = 'encoder_' +str(motor_number) +'_pos'
        return self.read_value(addressname)[0]
        
    def motor_status(self, motor_number, bit_num):
        addressname = 'status_m' + str(motor_number)
        s = self.read_value(addressname)[0]
        x = 1
        x = x << bit_num
        value = x & s
        value = value >> bit_num
        return value

    def tasks(self, motor_number):
        addressname = 'tasks_running_m' + str(motor_number)
        return self.read_value(addressname)[0]

    def pid(self, pid, target, value):
        addressname = str(pid) + '_' + str(target)
        self.write_value(addressname, (value, ))

    def pass_count(self, value):
        self.write_value('pass_count', (value, ))
        
    def tolerance(self, value):
        self.write_value('tolerance', (value, ))
        
MMX.add_compatible_sensor(None, 'mndsnsrs', 'NxTMMX') #Tested with version 'V1.01'


class HidCommand:
    TRANSMIT_DATA_TO_HOST = 'T'
    DEVICE_ASCII_DATA_MODE = 'A'
    DEVICE_DIRECT_DATA_MODE = 'D'

class HID(BaseDigitalSensor):
    """Class for Human Interface Device sensors"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command'  :        (0x41, '<B'),
                        'modifier'  :       (0x42, '<B'),
                        'keyboard_data'  :  (0x43, '<B'),
                        })
    I2C_DEV = 0x04

    def __init__(self, brick, port, check_compatible=False):
        super(HID, self).__init__(brick, port, check_compatible)

    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))

    def modifier(self, mod):
        self.write_value('modifier', (mod, ))
        
    def write_data(self, data):
        data = ord(data)
        self.write_value('keyboard_data', (data, ))
                
HID.add_compatible_sensor(None, 'mndsnsrs', 'NXTHID') #Tested with version 'V1.02'


class PS2Command:
    POWER_ON = 'E'
    POWER_OFF = 'D'
    DIGITAL_MODE = 'A'
    ANALOG_MODE = 's'
    ADPA_ON = 'N'
    ADPA_OFF = 'O'

class PS2(BaseDigitalSensor):   
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command'  :        (0x41, '<B'),
                        'button_set_1':     (0x42, '<B'),
                        'button_set_2':     (0x43, '<B'),
                        'x_left_joystick':  (0x44, '<B'),
                        'y_left_joystick':  (0x45, '<B'),
                        'x_right_joystick': (0x46, '<B'),
                        'y_right_joystick': (0x47, '<B'),
                        })
    
    def __init__(self, brick, port, check_compatible=False):
        super(PS2, self).__init__(brick, port, check_compatible)
    
    def command(self, command):
        value = ord(command)
        self.write_value('command', (value, ))

    def get_joystick(self, xyz, lr):
        addressname = str(xyz) + '_' + str(lr) + '_joystick'
        return self.read_value(addressname)[0]

    def get_buttons(self, setnum):
        addressname = 'button_set_' + str(setnum)
        return self.read_value(addressname)[0]

PS2.add_compatible_sensor(None, 'mndsnsrs', 'PSPNX') #Tested with version 'V2.00'
