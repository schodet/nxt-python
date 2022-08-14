# nxt.sensor.hitechnic module -- Classes to read HiTechnic sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, melducky, Samuel Leeman-Munk
# Copyright (C) 2011  jerradgenson, Marcus Wanner
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

from nxt.sensor import Type, Mode
from .digital import BaseDigitalSensor
from .analog import BaseAnalogSensor
from enum import Enum
from typing import Dict, List


class Compass(BaseDigitalSensor):
    """Hitechnic compass sensor."""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'mode': (0x41, 'B'),
                        'heading': (0x42, 'B'),
                        'adder' : (0x43, 'B'),
    })
    
    class Modes:
        MEASUREMENT = 0x00
        CALIBRATION = 0x43
        CALIBRATION_FAILED = 0x02
    
    def get_heading(self):
        """Returns heading from North in degrees."""

        two_degree_heading = self.read_value('heading')[0]
        adder = self.read_value('adder')[0]
        heading = two_degree_heading * 2 + adder

        return heading
    
    get_sample = get_heading

    def get_relative_heading(self,target=0):
        rheading = self.get_sample()-target
        if rheading > 180:
            rheading -= 360
        elif rheading < -180:
            rheading += 360
        return rheading	
    
    def is_in_range(self,minval,maxval):
        """This deserves a little explanation:
if max > min, it's straightforward, but
if min > max, it switches the values of max and min
and returns true if heading is NOT between the new max and min
        """
        if minval > maxval:
            (maxval,minval) = (minval,maxval)
            inverted = True
        else:
            inverted = False
        heading = self.get_sample()
        in_range = (heading > minval) and (heading < maxval)
        #an xor handles the reversal
        #a faster, more compact way of saying
        #if !reversed return in_range
        #if reversed return !in_range
        return bool(inverted) ^ bool(in_range) 

    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
         if mode != self.Modes.MEASUREMENT and \
                 mode != self.Modes.CALIBRATION:
             raise ValueError('Invalid mode specified: ' + str(mode))
         self.write_value('mode', (mode, ))
         
Compass.add_compatible_sensor(None, 'HiTechnc', 'Compass ') #Tested with version '\xfdV1.23  '
Compass.add_compatible_sensor(None, 'HITECHNC', 'Compass ') #Tested with version '\xfdV2.1   '


class Accelerometer(BaseDigitalSensor):
    'Object for Accelerometer sensors. Thanks to Paulo Vieira.'
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'x_axis_high': (0x42, 'b'),
        'y_axis_high': (0x43, 'b'),
        'z_axis_high': (0x44, 'b'),
        'xyz_short': (0x42, '3b'),
        'all_data': (0x42, '3b3B')
    })
    
    class Acceleration:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z
    
    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_acceleration(self):
        """Returns the acceleration along x, y, z axes. 200 => 1g.
        """
        xh, yh, zh, xl, yl, zl = self.read_value('all_data')
        x = xh << 2 | xl
        y = yh << 2 | yl
        z = zh << 2 | zl
        return self.Acceleration(x, y, z)
    
    get_sample = get_acceleration

Accelerometer.add_compatible_sensor(None, 'HiTechnc', 'Accel.  ')
Accelerometer.add_compatible_sensor(None, 'HITECHNC', 'Accel.  ') #Tested with version '\xfdV1.1   '


class IRReceiver(BaseDigitalSensor):
    """Object for HiTechnic IRReceiver sensors for use with LEGO Power Functions IR
Remotes. Coded to HiTechnic's specs for the sensor but not tested. Please report
whether this worked for you or not!
    """
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'm1A': (0x42, 'b'),
        'm1B': (0x43, 'b'),
        'm2A': (0x44, 'b'),
        'm2B': (0x45, 'b'),
        'm3A': (0x46, 'b'),
        'm3B': (0x47, 'b'),
        'm4A': (0x48, 'b'),
        'm4B': (0x49, 'b'),
        'all_data': (0x42, '8b')
    })

    class SpeedReading:
        def __init__(self, m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B):
            self.m1A, self.m1B, self.m2A, self.m2B, self.m3A, self.m3B, self.m4A, self.m4B = m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B
            self.channel_1 = (m1A, m1B)
            self.channel_2 = (m2A, m2B)
            self.channel_3 = (m3A, m3B)
            self.channel_4 = (m4A, m4B)
    
    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_speeds(self):
        """Returns the motor speeds for motors A and B on channels 1-4.
Values are -128, -100, -86, -72, -58, -44, -30, -16, 0, 16, 30, 44, 58, 72, 86
and 100. -128 specifies motor brake mode. Note that no motors are actually
being controlled here!
        """
        m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B = self.read_value('all_data')
        return self.SpeedReading(m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B)
    
    get_sample = get_speeds

IRReceiver.add_compatible_sensor(None, 'HiTechnc', 'IRRecv  ')
IRReceiver.add_compatible_sensor(None, 'HITECHNC', 'IRRecv  ')


class IRSeekerv2(BaseDigitalSensor):
    """Object for HiTechnic IRSeeker sensors. Coded to HiTechnic's specs for the sensor
but not tested. Please report whether this worked for you or not!
    """
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'dspmode': (0x41, 'B'),
        'DC_direction': (0x42, 'B'),
        'DC_sensor_1': (0x43, 'B'),
        'DC_sensor_2': (0x44, 'B'),
        'DC_sensor_3': (0x45, 'B'),
        'DC_sensor_4': (0x46, 'B'),
        'DC_sensor_5': (0x47, 'B'),
        'DC_sensor_mean': (0x48, 'B'),
        'all_DC': (0x42, '7B'),
        'AC_direction': (0x49, 'B'),
        'AC_sensor_1': (0x4A, 'B'),
        'AC_sensor_2': (0x4B, 'B'),
        'AC_sensor_3': (0x4C, 'B'),
        'AC_sensor_4': (0x4D, 'B'),
        'AC_sensor_5': (0x4E, 'B'),
        'all_AC': (0x49, '6B')
    })
    I2C_DEV = 0x10 #different from standard 0x02
    
    class DSPModes:
        #Modes for modulated (AC) data.
        AC_DSP_1200Hz = 0x00
        AC_DSP_600Hz = 0x01
    
    class _data:
        def get_dir_brightness(self, direction):
            "Gets the brightness of a given direction (1-9)."
            if direction%2 == 1: #if it's an odd number
                val = getattr(self, "sensor_%d" % ((direction-1)//2+1))
            else:
                val = (getattr(self, f"sensor_{direction // 2}")
                       + getattr(self, f"sensor_{direction // 2 + 1}")) / 2
            return val
    
    class DCData(_data):
        def __init__(self, direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean):
            self.direction, self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4, self.sensor_5, self.sensor_mean = direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean
    
    class ACData(_data):
        def __init__(self, direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5):
            self.direction, self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4, self.sensor_5 = direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5
            
    
    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_dc_values(self):
        """Returns the unmodulated (DC) values.
        """
        direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean = self.read_value('all_DC')
        return self.DCData(direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean)
    
    def get_ac_values(self):
        """Returns the modulated (AC) values. 600Hz and 1200Hz modes can be selected
between by using the set_dsp_mode() function.
        """
        direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5 = self.read_value('all_AC')
        return self.ACData(direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5)
    
    def get_dsp_mode(self):
        return self.read_value('dspmode')[0]
    
    def set_dsp_mode(self, mode):
        self.write_value('dspmode', (mode, ))
    
    get_sample = get_ac_values

IRSeekerv2.add_compatible_sensor(None, 'HiTechnc', 'NewIRDir')
IRSeekerv2.add_compatible_sensor(None, 'HITECHNC', 'NewIRDir')


class EOPD(BaseAnalogSensor):
    """Object for HiTechnic Electro-Optical Proximity Detection sensors.
    """
    
    # To be divided by processed value.
    _SCALE_CONSTANT = 250

    # Maximum distance the sensor can detect.
    _MAX_DISTANCE = 1023

    def __init__(self, brick, port):
        super().__init__(brick, port)
        from math import sqrt
        self.sqrt = sqrt

    def set_range_long(self):
        ''' Choose this mode to increase the sensitivity
            of the EOPD sensor by approximately 4x. May
            cause sensor overload.
            '''

        self.set_input_mode(Type.LIGHT_ACTIVE, Mode.RAW)

    def set_range_short(self):
        ''' Choose this mode to prevent the EOPD sensor from
            being overloaded by white objects.
           '''

        self.set_input_mode(Type.LIGHT_INACTIVE, Mode.RAW)
    
    def get_raw_value(self):
        '''Unscaled value read from sensor.'''

        return self._MAX_DISTANCE - self.get_input_values().raw_value
    
    def get_processed_value(self):
        '''Derived from the square root of the raw value.'''

        return self.sqrt(self.get_raw_value())

    def get_scaled_value(self):
        ''' Returns a value that will scale linearly as distance
            from target changes. This is the method that should
            generally be called to get EOPD sensor data.
            '''

        try:
            result = self._SCALE_CONSTANT / self.get_processed_value()
            return result

        except ZeroDivisionError:
            return self._SCALE_CONSTANT
    
    get_sample = get_scaled_value


class Colorv2(BaseDigitalSensor):
    """Object for HiTechnic Color v2 Sensors. Coded to HiTechnic's specs for the sensor
but not tested. Please report whether this worked for you or not!"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'mode': (0x41, 'B'),
        'number': (0x42, 'B'),
        'red': (0x43, 'B'),
        'green': (0x44, 'B'),
        'blue': (0x45, 'B'),
        'white': (0x46, 'B'),
        'index': (0x47, 'B'),
        'normred': (0x48, 'B'),
        'normgreen': (0x49, 'B'),
        'normblue': (0x4A, 'B'),
        'all_data': (0x42, '9B'),
        'rawred': (0x42, '<H'),
        'rawgreen': (0x44, '<H'),
        'rawblue': (0x46, '<H'),
        'rawwhite': (0x48, '<H'),
        'all_raw_data': (0x42, '<4H')
    })
    
    class Modes:
        ACTIVE = 0x00 #get measurements using get_active_color
        PASSIVE = 0x01 #get measurements using get_passive_color
        RAW = 0x03 #get measurements using get_passive_color
        BLACK_CALIBRATION = 0x42 #hold away from objects, results saved in EEPROM
        WHITE_CALIBRATION = 0x43 #hold in front of white surface, results saved in EEPROM
        LED_POWER_LOW = 0x4C #saved in EEPROM, must calibrate after using
        LED_POWER_HIGH = 0x48 #saved in EEPROM, must calibrate after using
        RANGE_NEAR = 0x4E #saved in EEPROM, only affects active mode
        RANGE_FAR = 0x46 #saved in EEPROM, only affects active mode, more susceptable to noise
        FREQ_50 = 0x35 #saved in EEPROM, use when local wall power is 50Hz
        FREQ_60 = 0x36 #saved in EEPROM, use when local wall power is 60Hz

    class ActiveData:
        def __init__(self, number, red, green, blue, white, index, normred, normgreen, normblue):
            self.number, self.red, self.green, self.blue, self.white, self.index, self.normred, self.normgreen, self.normblue = number, red, green, blue, white, index, normred, normgreen, normblue

    class PassiveData:
        #also holds raw mode data
        def __init__(self, red, green, blue, white):
            self.red, self.green, self.blue, self.white = red, green, blue, white
    
    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_active_color(self):
        """Returns color values when in active mode.
        """
        number, red, green, blue, white, index, normred, normgreen, normblue = self.read_value('all_data')
        return self.ActiveData(number, red, green, blue, white, index, normred, normgreen, normblue)
    
    get_sample = get_active_color
    
    def get_passive_color(self):
        """Returns color values when in passive or raw mode.
        """
        red, green, blue, white = self.read_value('all_raw_data')
        return self.PassiveData(red, green, blue, white)
    
    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
        self.write_value('mode', (mode, ))

Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD ')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD ')


class Gyro(BaseAnalogSensor):
    'Object for gyro sensors'
#This class is for the hitechnic gryo sensor. When the gryo is not
#moving there will be a constant offset that will change with 
#temperature and other ambient factors. The calibrate() function
#takes the currect value and uses it to offset subsequesnt ones.

    def __init__(self, brick, port):
        super().__init__(brick, port)
        self.set_input_mode(Type.ANGLE, Mode.RAW)
        self.offset = 0
    
    def get_rotation_speed(self):
        return self.get_input_values().scaled_value - self.offset
    
    def set_zero(self, value):
        self.offset = value
    
    def calibrate(self):
        self.set_zero(self.get_rotation_speed())
    
    get_sample = get_rotation_speed


class Prototype(BaseDigitalSensor):
    """Object for HiTechnic sensor prototype boards."""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'A0': (0x42, '<H'),
        'A1': (0x44, '<H'),
        'A2': (0x46, '<H'),
        'A3': (0x48, '<H'),
        'A4': (0x4A, '<H'),
        'all_analog': (0x42, '<5H'),
        'digital_in': (0x4C, 'B'),
        'digital_out': (0x4D, 'B'),
        'digital_cont': (0x4E, 'B'),
        'sample_time': (0x4F, 'B'),
        })
    
    class Digital_Data():
        """Container for 6 bits of digital data. Takes an integer or a list of six bools
and can be converted into a list of bools or an integer."""
        def __init__(self, pins):
            if isinstance(pins, int):
                self.dataint = pins
                self.datalst = self.tolist(pins)
            else:
                self.dataint = self.toint(pins)
                self.datalst = pins
            self.d0, self.d1, self.d2, self.d3, self.d4, self.d5 = self.datalst
        
        def tolist(self, val):
            lst = []
            for i in range(6):
                lst.append(bool(val & 2**i))
            return lst

        def toint(self, lst):
            val = 0
            for i in range(6):
                val += int(bool(lst[i])) * (2**i)
            return val
        
        def __int__(self):
            return self.dataint
        
        def __iter__(self):
            return iter(self.datalst)
        
        def __getitem__(self, i):
            return self.datalst[i]
    
    class Analog_Data():
        def __init__(self, a0, a1, a2, a3, a4):
            self.a0, self.a1, self.a2, self.a3, self.a4 = a0, a1, a2, a3, a4
    
    def get_analog(self):
        return self.Analog_Data(*self.read_value('all_analog'))
    
    def get_digital(self):
        return self.Digital_Data(self.read_value('digital_in')[0])
    
    def set_digital(self, pins):
        """Can take a Digital_Data() object"""
        self.write_value('digital_out', (int(pins), ))
    
    def set_digital_modes(self, modes):
        """Sets input/output mode of digital pins. Can take a Digital_Data() object."""
        self.write_value('digital_cont', (int(modes), ))


Prototype.add_compatible_sensor(None, 'HiTechnc', 'Proto   ')


class SuperPro(BaseDigitalSensor):
    """
    Object for HiTechnic sensor SuperPro boards.
    """
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        "version": (0x00, "8s"),
        "manufacturer": (0x08, "8s"),
        "sensor_type": (0x10, "8s"),
        "analog_a0": (0x42, "<H"),
        "analog_a1": (0x44, "<H"),
        "analog_a2": (0x46, "<H"),
        "analog_a3": (0x48, "<H"),
        "digital_in": (0x4C, "<B"),
        "digital_out": (0x4D, "<B"),
        "digital_dir": (0x4E, "<B"),
        "strobe_out": (0x50, "B"),
        "led_out": (0x51, "B"),
        "analog_out0_mode": (0x52, "B"),
        "analog_out0_freq": (0x53, "<H"),
        "analog_out0_volts": (0x55, "H"),
        "analog_out1_mode": (0x57, "B"),
        "analog_out1_freq": (0x58, "<H"),
        "analog_out1_volts": (0x5A, "H")
    })

    I2C_DEV = 0x10

    # Used for converting ADC bits into percent signal
    ANALOG_LSB = 1 / 1023

    class AnalogOutputMode(Enum):
        DC = 0
        SINE = 1
        SQUARE = 2
        UPWARDS_SAWTOOTH = 3
        DOWNWARDS_SAWTOOTH = 4
        TRIANGLE = 5
        PWM = 6  # TODO: Test. Documentation seems to imply this should work, but it wasn't for me.

    def get_analog(self) -> Dict[str, int]:
        """
        Get analog input pins (A0-A3) result in raw bits

        :return: Map of pin name, pin value (bits)
        """
        analog_in_pin_name_map = [("analog_a0", "a0"), ("analog_a1", "a1"), ("analog_a2", "a2"), ("analog_a3", "a3")]
        analog_raw_map = {}
        for pin in analog_in_pin_name_map:
            raw = self.read_value(pin[0])[0]
            # Not 100% sure about this logic but seems to work.
            low = (raw & 0xFF00) >> 8
            high = raw & 0x00FF
            analog_input = low + high * 4
            analog_raw_map[pin[1]] = analog_input
        return analog_raw_map

    def get_analog_volts(self, voltage_reference: float = 3.3) -> Dict[str, float]:
        """
        Get analog input pins (A0-A3) results in volts. Resolution to ~3mV (voltage reference * (1/1023) volts)

        :param voltage_reference: optionally provide measured voltage from 3.3V regulator for more accurate calculations
        :return: Map of pin name, pin voltage (in volts)
        """
        analog_raw_map = self.get_analog()
        analog_voltage_map = {}
        for item in analog_raw_map:
            analog_voltage_map[item] = analog_raw_map[item] * self.ANALOG_LSB * voltage_reference
        return analog_voltage_map

    @staticmethod
    def _byte_to_boolean_list(integer: int, reverse=False) -> List[bool]:
        # Converts byte to boolean string, inverts string to correct bit order if needed, converts chars to boolean list
        if reverse:
            return [bit == "1" for bit in "{0:08b}".format(integer)[::-1]]
        return [bit == "1" for bit in "{0:08b}".format(integer)]

    @staticmethod
    def _boolean_list_to_byte(boolean_list: List[bool], reverse=False) -> int:
        if len(boolean_list) != 8:
            raise RuntimeError("List must be 8 booleans in length")
        if reverse:
            boolean_list.reverse()
        output_byte = 0
        for bit in range(0, 8):
            output = (2 ** bit) * boolean_list[bit]
            output_byte += output
        return output_byte

    def get_digital(self) -> Dict[str, bool]:
        """
        Get digital input pins (D0-D7)

        :return: Boolean list, LSB first.
        """
        digital_in = self.read_value("digital_in")[0]
        boolean_list = self._byte_to_boolean_list(digital_in, reverse=True)
        digital_in_map = {}
        for x in range(0, 8):
            digital_in_map["b{}".format(x)] = boolean_list[x]
        return digital_in_map

    def set_digital(self, pins: List[bool]):
        """
        Set digital output pins (D0-D7)

        :param pins: boolean list (LSB first)
        """
        if len(pins) != 8:
            raise RuntimeError("Need to specify list of 8 boolean values")
        self.write_value("digital_out", [self._boolean_list_to_byte(pins)])

    def set_digital_byte(self, integer: int, lsb=True):
        """
        Set digital output pins (D0-D7) from byte

        :param integer: Byte (0-255 inclusive)
        :param lsb: Whether to output in LSB order (0x01 = pin B0)
        """
        if not (0 <= integer <= 255):
            raise RuntimeError("Integer must be in range of 0 to 255 inclusive")
        self.set_digital(self._byte_to_boolean_list(integer, reverse=lsb))

    def set_digital_modes(self, modes: List[bool]):
        """
        Set digital pin mode (D0-D7)

        :param modes: boolean list (LSB first, True = Output, False = Input)
        """
        if len(modes) != 8:
            raise RuntimeError("Need to specify list of 8 boolean values")
        self.write_value("digital_dir", [self._boolean_list_to_byte(modes)])

    def set_digital_modes_byte(self, mode_int: int, lsb=True):
        """
        Set digital output pins mode (D0-D7) from byte

        :param mode_int: Byte (0-255 inclusive)
        :param lsb: Whether to output in LSB order (0x01 = pin B0)
        """
        if not (0 <= mode_int <= 255):
            raise RuntimeError("Integer must be in range of 0 to 255 inclusive")
        self.set_digital_modes(self._byte_to_boolean_list(mode_int, reverse=lsb))

    def set_strobe_output(self, mode_int: int):
        """
        Strobe output - behaves like any other output, but has strobe signal sent whenever a digital read/write sent.
        When a digital read is done, it will send a spike on RD (inverse of the current RD pin state),
        when a digital write is done, it will send a spike on WR (inverse of the current WR pin state)
        This 'digital read' and 'digital write' actions causing a spike applies to the B0-7 pins
        Bits to write: S0 = 1, S1 = 2 S2 = 4 S3 = 8 RD = 16 WR = 32

        :param mode_int: mode_int: Byte (0-63 inclusive)
        """
        if not (0 <= mode_int <= 255):
            raise RuntimeError("Integer must be in range of 0 to 255 inclusive")
        self.write_value("strobe_out", [mode_int])

    def set_led_output(self, red=False, blue=False):
        """
        Set LED output. True = On, False = Off

        :param red: Boolean for Red LED
        :param blue: Boolean for Blue LED
        """
        output_byte = (red * 0x01) + (blue * 0x02)
        self.write_value("led_out", [output_byte])

    def analog_out(self, pin: int, mode: AnalogOutputMode, freq: int, voltage_bits: int):
        """
        Analog Output Pins

        :param pin: 0 for O0, 1 for O1
        :param mode: 0-5 for various modes, see AnalogOutputMode class
        :param freq: 0 to 2^13Hz (~8kHz) Note: if 0 provided for wave, will get 1Hz.
        :param voltage_bits: 0-1023 for 0V to 3.3V (ish)
        """
        if not 0 <= pin <= 1:
            raise RuntimeError("Pin must be 0 or 1")
        if not 0 <= voltage_bits <= ((2 ** 10) - 1):
            raise RuntimeError("Integer must be in range of 0 and (2^10)-1 inclusive")
        low = voltage_bits & 0b0000000000000011
        low_shifted = low << 8
        high = voltage_bits & 0b0000001111111100
        high_shifted = high >> 2
        actual_voltage_bits = low_shifted | high_shifted
        freq_swapped = (0xFF00 & freq) >> 8
        freq_swapped += (0x00FF & freq) << 8
        if pin != 0:
            self.write_value("analog_out1_mode", [mode.value])
            self.write_value("analog_out1_freq", [freq_swapped])
            self.write_value("analog_out1_volts", [actual_voltage_bits])
        else:
            self.write_value("analog_out0_mode", [mode.value])
            self.write_value("analog_out0_freq", [freq_swapped])
            self.write_value("analog_out0_volts", [actual_voltage_bits])

    def analog_out_voltage(self, pin: int, mode: AnalogOutputMode, freq: int, voltage: float, voltage_reference=3.3):
        """
        Analog Output Pins

        :param pin: 0 for O0, 1 for O1
        :param mode: 0-5 for various modes, see AnalogOutputMode class
        :param freq: 0 to 2^13Hz (~8kHz) Note: if 0 provided for wave, will get 1Hz
        :param voltage: The desired voltage (between 0 and the voltage reference)
        :param voltage_reference: Output 1023 in the analog_out mode to find the maximum voltage, enter it here.
        """
        if not 0 <= pin <= 1:
            raise RuntimeError("Pin must be 0 or 1")
        voltage_percentile = voltage / voltage_reference
        voltage_bits = int(voltage_percentile * 1023)
        self.analog_out(pin, mode, freq, voltage_bits)


SuperPro.add_compatible_sensor(None, 'HiTechnc', 'SuperPro')


class ServoCon(BaseDigitalSensor):
    """Object for HiTechnic FIRST Servo Controllers. Coded to HiTechnic's specs for
the sensor but not tested. Please report whether this worked for you or not!"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'status': (0x40, 'B'),
        'steptime': (0x41, 'B'),
        's1pos': (0x42, 'B'),
        's2pos': (0x43, 'B'),
        's3pos': (0x44, 'B'),
        's4pos': (0x45, 'B'),
        's5pos': (0x46, 'B'),
        's6pos': (0x47, 'B'),
        'pwm': (0x48, 'B'),
    })
    
    class Status:
        STOPPED = 0x00 #all motors stopped
        RUNNING = 0x01 #motor(s) moving

    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_status(self):
        """Returns the status of the motors. 0 for all stopped, 1 for
some running.
        """
        return self.read_value('status')[0]
    
    def set_step_time(self, time):
        """Sets the step time (0-15).
        """
        self.write_value('steptime', (time, ))
    
    def set_pos(self, num, pos):
        """Sets the position of a server. num is the servo number (1-6),
pos is the position (0-255).
        """
        self.write_value('s%dpos' % num, (pos, ))
    
    def get_pwm(self):
        """Gets the "PWM enable" value. The function of this value is
nontrivial and can be found in the documentation for the sensor.
        """
        return self.read_value('pwm')[0]
    
    def set_pwm(self, pwm):
        """Sets the "PWM enable" value. The function of this value is
nontrivial and can be found in the documentation for the sensor.
        """
        self.write_value('pwm', (pwm, ))

ServoCon.add_compatible_sensor(None, 'HiTechnc', 'ServoCon')


class MotorCon(BaseDigitalSensor):
    """Object for HiTechnic FIRST Motor Controllers."""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'm1enctarget': (0x40, '>l'),
        'm1mode': (0x44, 'B'),
        'm1power': (0x45, 'b'),
        'm2power': (0x46, 'b'),
        'm2mode': (0x47, 'B'),
        'm2enctarget': (0x48, '>l'),
        'm1enccurrent': (0x4c, '>l'),
        'm2enccurrent': (0x50, '>l'),
        'batteryvoltage': (0x54, '2B'),
        'm1gearratio': (0x56, 'b'),
        'm1pid': (0x57, '3B'),
        'm2gearratio': (0x5a, 'b'),
        'm2pid': (0x5b, '3B'),
    })
    
    class PID_Data():
        def __init__(self, p, i, d):
            self.p, self.i, self.d = p, i, d
    
    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)
    
    def set_enc_target(self, mot, val):
        """Set the encoder target (-2147483648-2147483647) for a motor
        """
        self.write_value('m%denctarget'%mot, (val, ))
    
    def get_enc_target(self, mot):
        """Get the encoder target for a motor
        """
        return self.read_value('m%denctarget'%mot)[0]
    
    def get_enc_current(self, mot):
        """Get the current encoder value for a motor
        """
        return self.read_value('m%denccurrent'%mot)[0]
    
    def set_mode(self, mot, mode):
        """Set the mode for a motor. This value is a bit mask and you can
find details about it in the sensor's documentation.
        """
        self.write_value('m%dmode'%mot, (mode, ))
    
    def get_mode(self, mot):
        """Get the mode for a motor. This value is a bit mask and you can
find details about it in the sensor's documentation.
        """
        return self.read_value('m%dmode'%mot)[0]
    
    def set_power(self, mot, power):
        """Set the power (-100-100) for a motor
        """
        self.write_value('m%dpower'%mot, (power, ))
    
    def get_power(self, mot):
        """Get the power for a motor
        """
        return self.read_value('m%dpower'%mot)[0]
    
    def set_gear_ratio(self, mot, ratio):
        """Set the gear ratio for a motor
        """
        self.write_value('m%dgearratio'%mot, (ratio, ))
    
    def get_gear_ratio(self, mot):
        """Get the gear ratio for a motor
        """
        return self.read_value('m%dgearratio'%mot)[0]
    
    def set_pid(self, mot, piddata):
        """Set the PID coefficients for a motor. Takes data in
MotorCon.PID_Data(p, i, d) format.
        """
        self.write_value('m%dpid'%mot, (piddata.p, piddata.i, piddata.d))
    
    def get_pid(self, mot):
        """Get the PID coefficients for a motor. Returns a PID_Data() object.
        """
        p, i, d = self.read_value('m%dpid'%mot)
        return self.PID_Data(p, i, d)
    
    def get_battery_voltage(self):
        """Gets the battery voltage (in millivolts/20)
        """
        data = self.read_value('batteryvoltage')
        high = data[0]
        low = data[1]
        return high << 2 | low

MotorCon.add_compatible_sensor(None, 'HiTechnc', 'MotorCon')


class Angle(BaseDigitalSensor):
    """HiTechnic Angle Sensor."""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'mode': (0x41, 'c'),
        'angle': (0x42, '2B'),
        'angle_acc': (0x44, '>l'),
        'rpm': (0x48, '>h'),
    })

    def get_angle(self):
        v = self.read_value('angle')
        return v[0] * 2 + v[1]

    get_sample = get_angle

    def get_accumulated_angle(self):
        return self.read_value("angle_acc")[0]

    def get_rpm(self):
        return self.read_value("rpm")[0]

    def calibrate(self):  #Current angle will be zero degrees written in EEPROM
        self.write_value('mode', b'C')

    def reset(self):    #Reset accumulated angle
        self.write_value('mode', b'R')
