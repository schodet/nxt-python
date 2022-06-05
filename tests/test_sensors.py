# test_sensors -- Test nxt.sensor modules
# Copyright (C) 2021  Nicolas Schodet
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
import struct
from unittest.mock import Mock, call

import pytest

import nxt.sensor
import nxt.sensor.analog
import nxt.sensor.digital
import nxt.sensor.generic
import nxt.sensor.hitechnic
import nxt.sensor.mindsensors
from nxt.sensor import Mode, Port, Type


@pytest.fixture
def mdigital(monkeypatch):
    m = Mock(spec_set=("read_value", "write_value"))
    monkeypatch.setattr(
        nxt.sensor.digital.BaseDigitalSensor, "read_value", m.read_value
    )
    monkeypatch.setattr(
        nxt.sensor.digital.BaseDigitalSensor, "write_value", m.write_value
    )
    return m


class TestGeneric:
    """Test non digital sensors."""

    def test_analog(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.analog.BaseAnalogSensor)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.SWITCH, Mode.BOOL, 1, 2, 3, 4),
        ]
        s.set_input_mode(Type.SWITCH, Mode.BOOL)
        v = s.get_input_values()
        assert v.port == Port.S1
        assert v.valid is True
        assert v.calibrated is False
        assert v.sensor_type == Type.SWITCH
        assert v.mode == Mode.BOOL
        assert v.raw_value == 1
        assert v.normalized_value == 2
        assert v.scaled_value == 3
        assert v.calibrated_value == 4
        assert str(v).startswith("(")
        s.reset_input_scaled_value()
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.SWITCH, Mode.BOOL),
            call.get_input_values(Port.S1),
            call.reset_input_scaled_value(Port.S1),
        ]

    def test_touch(self, mbrick):
        assert (
            nxt.sensor.generic.Touch.get_sample is nxt.sensor.generic.Touch.is_pressed
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.generic.Touch)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.SWITCH, Mode.BOOL, 1023, 1023, 0, 1023),
            (Port.S1, True, False, Type.SWITCH, Mode.BOOL, 183, 183, 1, 183),
        ]
        assert s.is_pressed() is False
        assert s.is_pressed() is True
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.SWITCH, Mode.BOOL),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
        ]

    def test_light(self, mbrick):
        assert (
            nxt.sensor.generic.Light.get_sample
            is nxt.sensor.generic.Light.get_lightness
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.generic.Light)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 726, 250, 250, 250),
            (Port.S1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 823, 107, 107, 107),
        ]
        assert s.get_lightness() == 250
        s.set_illuminated(False)
        assert s.get_lightness() == 107
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LIGHT_ACTIVE, Mode.RAW),
            call.get_input_values(Port.S1),
            call.set_input_mode(Port.S1, Type.LIGHT_INACTIVE, Mode.RAW),
            call.get_input_values(Port.S1),
        ]

    def test_sound(self, mbrick):
        assert (
            nxt.sensor.generic.Sound.get_sample is nxt.sensor.generic.Sound.get_loudness
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.generic.Sound)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.SOUND_DBA, Mode.RAW, 999, 15, 15, 15),
            (Port.S1, True, False, Type.SOUND_DB, Mode.RAW, 999, 15, 15, 15),
        ]
        assert s.get_loudness() == 15
        s.set_adjusted(False)
        assert s.get_loudness() == 15
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.SOUND_DBA, Mode.RAW),
            call.get_input_values(Port.S1),
            call.set_input_mode(Port.S1, Type.SOUND_DB, Mode.RAW),
            call.get_input_values(Port.S1),
        ]

    def test_color(self, mbrick):
        assert nxt.sensor.generic.Color.get_sample is nxt.sensor.generic.Color.get_color
        s = mbrick.get_sensor(Port.S1, nxt.sensor.generic.Color)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.COLOR_FULL, Mode.RAW, 0, 0, 4, 0),
            (Port.S1, True, False, Type.COLOR_FULL, Mode.RAW, 0, 0, 4, 0),
            # TODO: handle invalid measures on configuration change.
            (Port.S1, True, False, Type.COLOR_RED, Mode.RAW, 114, 46, 46, 46),
            (Port.S1, True, False, Type.COLOR_RED, Mode.RAW, 114, 46, 46, 46),
        ]
        color = s.get_color()
        assert color == 4
        assert color == s.DetectedColor.YELLOW
        assert s.get_reflected_light(Type.COLOR_RED) == 46
        assert s.get_light_color() == Type.COLOR_RED
        assert mbrick.mock_calls == [
            # TODO: set too much input mode.
            call.set_input_mode(Port.S1, Type.COLOR_FULL, Mode.RAW),
            call.set_input_mode(Port.S1, Type.COLOR_FULL, Mode.RAW),
            # TODO: get too much input values.
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.set_input_mode(Port.S1, Type.COLOR_RED, Mode.RAW),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
        ]


@pytest.mark.usefixtures("mtime")
class TestDigital:
    """Test nxt.sensor.digital."""

    version_bin = b"V1.0\0\0\0\0"
    product_id_bin = b"LEGO\0\0\0\0"
    sensor_type_bin = b"Sonar\0\0\0"

    def test_get_sensor_info(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        mbrick.ls_get_status.return_value = 8
        mbrick.ls_read.side_effect = [
            self.version_bin,
            self.product_id_bin,
            self.sensor_type_bin,
        ]
        info = s.get_sensor_info()
        assert info.version == "V1.0"
        assert info.product_id == "LEGO"
        assert info.sensor_type == "Sonar"
        print(info)
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(Port.S1, bytes((0x02, 0x00)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            call.ls_write(Port.S1, bytes((0x02, 0x10)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
        ]

    def test_check_compatible(self, mbrick, caplog):
        class DummySensor(nxt.sensor.digital.BaseDigitalSensor):
            pass

        DummySensor.add_compatible_sensor(None, "NXT-PYTH", "Dummy")
        mbrick.ls_get_status.return_value = 8
        mbrick.ls_read.side_effect = [
            b"V3\0\0\0\0\0\0",
            b"NXT-PYTH",
            b"Dummy\0\0\0",
            b"V2\0\0\0\0\0\0",
            b"NXT-PYTH",
            b"Plop\0\0\0\0",
        ]
        DummySensor(mbrick, Port.S1)
        assert "WARNING" not in caplog.text
        DummySensor(mbrick, Port.S2)
        assert "WARNING" in caplog.text

    def test_write_value(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        s.I2C_ADDRESS = dict(s.I2C_ADDRESS, command=(0x41, "B"))
        s.write_value("command", (0x12,))
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(Port.S1, bytes((0x02, 0x41, 0x12)), 0),
        ]

    def test_not_ready(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        mbrick.ls_get_status.side_effect = [nxt.error.I2CPendingError("pending"), 8]
        mbrick.ls_read.return_value = self.product_id_bin
        assert s.read_value("product_id") == (self.product_id_bin,)
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
        ]

    def test_status_timeout(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        mbrick.ls_get_status.side_effect = (
            [nxt.error.I2CPendingError("pending")] * 30 * 3
        )
        with pytest.raises(nxt.error.I2CError):
            s.read_value("product_id")
        mock_calls = [call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW)] + (
            [call.ls_write(Port.S1, bytes((0x02, 0x08)), 8)]
            + [call.ls_get_status(Port.S1)] * 30
            + [call.ls_read(Port.S1)]
        ) * 3
        assert mbrick.mock_calls == mock_calls

    def test_read_error(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        mbrick.ls_get_status.side_effect = [8, 8]
        mbrick.ls_read.side_effect = [self.product_id_bin[1:], self.product_id_bin]
        assert s.read_value("product_id") == (self.product_id_bin,)
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            # Retry.
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
        ]

    def test_read_timeout(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.digital.BaseDigitalSensor, False)
        mbrick.ls_get_status.return_value = 8
        mbrick.ls_read.return_value = self.product_id_bin[1:]
        with pytest.raises(nxt.error.I2CError):
            s.read_value("product_id")
        mock_calls = [call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW)] + [
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
        ] * 3
        assert mbrick.mock_calls == mock_calls

    def test_find_class(self):
        def test(info, cls):
            found = nxt.sensor.digital.find_class(nxt.sensor.digital.SensorInfo(*info))
            assert found is cls

        test(("V1.0", "LEGO", "Sonar"), nxt.sensor.generic.Ultrasonic)
        test(("Vx.xx", "mndsnsrs", "CMPS"), nxt.sensor.mindsensors.Compassv2)
        test(("Vx.xx", "mndsnsrs", "DIST"), nxt.sensor.mindsensors.DIST)
        test(("V3.20", "mndsnsrs", "ACCL-NX"), nxt.sensor.mindsensors.ACCL)
        test(("V2.11", "mndsnsrs", "MTRMUX"), nxt.sensor.mindsensors.MTRMUX)
        test(("V1.16", "mndsnsrs", "LineLdr"), nxt.sensor.mindsensors.LineLeader)
        test(("V1.20", "mndsnsrs", "NXTServo"), nxt.sensor.mindsensors.Servo)
        test(("V1.01", "mndsnsrs", "NxTMMX"), nxt.sensor.mindsensors.MMX)
        test(("V1.02", "mndsnsrs", "NXTHID"), nxt.sensor.mindsensors.HID)
        test(("V2.00", "mndsnsrs", "PSPNX"), nxt.sensor.mindsensors.PS2)
        test(("\xfdV1.23", "HiTechnc", "Compass "), nxt.sensor.hitechnic.Compass)
        test(("\xfdV2.1", "HITECHNC", "Compass "), nxt.sensor.hitechnic.Compass)
        test(
            ("\xfdV1.1   ", "HITECHNC", "Accel.  "), nxt.sensor.hitechnic.Accelerometer
        )
        test(("Vx.xx", "HITECHNC", "IRRecv  "), nxt.sensor.hitechnic.IRReceiver)
        test(("Vx.xx", "HITECHNC", "NewIRDir"), nxt.sensor.hitechnic.IRSeekerv2)
        test(("Vx.xx", "HITECHNC", "ColorPD"), nxt.sensor.hitechnic.Colorv2)
        test(("Vx.xx", "HITECHNC", "ColorPD "), nxt.sensor.hitechnic.Colorv2)
        test(("Vx.xx", "HiTechnc", "Proto   "), nxt.sensor.hitechnic.Prototype)
        test(("Vx.xx", "HiTechnc", "ServoCon"), nxt.sensor.hitechnic.ServoCon)
        test(("Vx.xx", "HiTechnc", "MotorCon"), nxt.sensor.hitechnic.MotorCon)

    def test_get_sensor(self, mbrick):
        mbrick.ls_get_status.return_value = 8
        mbrick.ls_read.side_effect = [
            self.version_bin,
            self.product_id_bin,
            self.sensor_type_bin,
        ]
        assert mbrick.get_sensor(Port.S1).__class__ is nxt.sensor.generic.Ultrasonic
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(Port.S1, bytes((0x02, 0x00)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            call.ls_write(Port.S1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            call.ls_write(Port.S1, bytes((0x02, 0x10)), 8),
            call.ls_get_status(Port.S1),
            call.ls_read(Port.S1),
            call.set_input_mode(Port.S1, Type.LOW_SPEED_9V, Mode.RAW),
        ]


class TestGenericDigital:
    """Test LEGO digital sensors."""

    def test_ultrasonic(self, mbrick, mdigital):
        assert (
            nxt.sensor.generic.Ultrasonic.get_sample
            is nxt.sensor.generic.Ultrasonic.get_distance
        )
        s = mbrick.get_sensor(
            Port.S1, nxt.sensor.generic.Ultrasonic, check_compatible=False
        )
        mdigital.read_value.side_effect = [
            (42,),
            (b"10E-2m\0",),
            (1, 2, 3, 4, 5, 6, 7, 8),
            (4,),
            (43,),
        ]
        assert s.get_distance() == 42
        assert s.get_measurement_units() == "10E-2m"
        assert s.get_all_measurements() == (1, 2, 3, 4, 5, 6, 7, 8)
        assert s.get_measurement_no(3) == 4
        s.command(s.Command.OFF)
        assert s.get_interval() == 43
        s.set_interval(44)
        assert mdigital.mock_calls == [
            call.read_value("measurement_byte_0"),
            call.read_value("measurement_units"),
            call.read_value("measurements"),
            call.read_value("measurement_byte_3"),
            call.write_value("command", (0,)),
            call.read_value("continuous_measurement_interval"),
            call.write_value("continuous_measurement_interval", (44,)),
        ]

    def test_temperature(self, mbrick, mdigital):
        assert (
            nxt.sensor.generic.Temperature.get_sample
            is nxt.sensor.generic.Temperature.get_deg_c
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.generic.Temperature)
        mdigital.read_value.side_effect = [
            (1600 * 16,),
            (1600 * 16,),
            struct.unpack(">h", b"\xff\x80"),
        ]
        assert s.get_deg_c() == 100
        assert s.get_deg_f() == 212
        assert s.get_deg_c() == -0.5
        assert mdigital.mock_calls == [
            call.read_value("raw_value"),
            call.read_value("raw_value"),
            call.read_value("raw_value"),
        ]


class TestMindsensors:
    """Test Mindsensors sensors."""

    def test_sumoeyes(self, mbrick):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.SumoEyes)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 0, 0, 0, 0),
            (Port.S1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 0, 350, 0, 0),
            (Port.S1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 0, 650, 0, 0),
            (Port.S1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 0, 800, 0, 0),
        ]
        m = s.get_sample()
        assert str(m) == "(left: False, right: False)"
        assert (m.left, m.right) == (False, False)
        m = s.get_sample()
        assert (m.left, m.right) == (True, False)
        m = s.get_sample()
        assert (m.left, m.right) == (False, True)
        m = s.get_sample()
        assert (m.left, m.right) == (True, True)
        s.set_long_range(True)
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LIGHT_ACTIVE, Mode.RAW),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.set_input_mode(Port.S1, Type.LIGHT_INACTIVE, Mode.RAW),
        ]

    def test_compassv2(self, mbrick, mdigital):
        assert (
            nxt.sensor.mindsensors.Compassv2.get_sample
            is nxt.sensor.mindsensors.Compassv2.get_heading
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.Compassv2, False)
        mdigital.read_value.return_value = (300,)
        # TODO: should return degrees (divide by 10).
        assert s.get_heading() == 300
        s.command(s.Commands.BEGIN_CALIBRATION)
        # TODO: get rid of ord, adapt format.
        assert mdigital.mock_calls == [
            call.write_value("command", (ord("I"),)),
            call.read_value("heading"),
            call.write_value("command", (ord("C"),)),
        ]

    def test_dist(self, mbrick, mdigital):
        assert (
            nxt.sensor.mindsensors.DIST.get_sample
            is nxt.sensor.mindsensors.DIST.get_distance
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.DIST, False)
        # TODO: get rid of ord, adapt format.
        mdigital.read_value.side_effect = [(100,), (ord("2"),), (42,), (43,), (44,)]
        assert s.get_distance() == 100
        assert s.get_type() == ord(s.Commands.TYPE_GP2D120)
        s.command(s.Commands.POWER_OFF)
        assert s.get_voltage() == 42
        assert s.get_min_distance() == 43
        assert s.get_max_distance() == 44
        assert mdigital.mock_calls == [
            call.read_value("distance"),
            call.read_value("type"),
            call.write_value("command", (ord("D"),)),
            call.read_value("voltage"),
            call.read_value("min_distance"),
            call.read_value("max_distance"),
        ]

    def test_rtc(self, mbrick, mdigital):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.RTC)
        # TODO: this one is completely broken:
        #  - Return str instead of int.
        #  - Bad handling of hour format.
        #  - Fields are read one by one (what happen if you read minutes at 11:59 and
        #    hours at 12:00?
        #  - Pretty sure struct_time is not right too.
        mdigital.read_value.side_effect = [(0x32,)]
        assert s.get_seconds() == "32"

    def test_accl(self, mbrick, mdigital):
        assert (
            nxt.sensor.mindsensors.ACCL.get_sample
            is nxt.sensor.mindsensors.ACCL.get_all_accel
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.ACCL, False)
        # TODO: get rid of ord, adapt format.
        mdigital.read_value.side_effect = [
            (ord("2"),),
            (42,),
            (1, 2, 3),
            (43,),
            (1, 2, 3),
            (44,),
            (45,),
        ]
        s.command(s.Commands.SENS_2G)
        assert s.get_sensitivity() == s.Commands.SENS_2G
        assert s.get_tilt("x") == 42
        assert s.get_all_tilt() == (1, 2, 3)
        assert s.get_accel("z") == 43
        assert s.get_all_accel() == (1, 2, 3)
        assert s.get_offset("x") == 44
        assert s.get_range("x") == 45
        s.set_offset("x", 46)
        s.set_range("x", 47)
        assert mdigital.mock_calls == [
            call.write_value("command", (ord("2"),)),
            call.read_value("sensitivity"),
            call.read_value("x_tilt"),
            call.read_value("all_tilt"),
            call.read_value("z_accel"),
            call.read_value("all_accel"),
            call.read_value("x_offset"),
            call.read_value("x_range"),
            call.write_value("x_offset", (46,)),
            call.write_value("x_range", (47,)),
        ]

    def test_mtrmux(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.mindsensors.MTRMUX, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.MTRMUX, False)
        mdigital.read_value.side_effect = [(1,), (2,)]
        s.command(s.Commands.FLOAT)
        s.set_direction(1, 1)
        s.set_speed(2, 2)
        assert s.get_direction(3) == 1
        assert s.get_speed(4) == 2
        assert mdigital.mock_calls == [
            call.write_value("command", (0,)),
            call.write_value("direction_m1", (1,)),
            call.write_value("speed_m2", (2,)),
            call.read_value("direction_m3"),
            call.read_value("speed_m4"),
        ]

    def test_lineleader(self, mbrick, mdigital):
        assert (
            nxt.sensor.mindsensors.LineLeader.get_sample
            is nxt.sensor.mindsensors.LineLeader.get_reading_all
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.LineLeader, False)
        mdigital.read_value.side_effect = [
            (-10,),
            (50,),
            (0x5A,),
            (50,),
            (1, 2, 3, 4, 5, 6, 7, 8),
            (60,),
            (11, 12, 13, 14, 15, 16, 17, 18),
        ]
        s.command(s.Commands.CALIBRATE_WHITE)
        assert s.get_steering() == -10
        assert s.get_average() == 50
        assert s.get_result() == 0x5A
        s.set_set_point(50)
        s.set_pid("p", 35)
        s.set_pid_divisor("i", 10)
        assert s.get_reading(1) == 50
        assert s.get_reading_all() == (1, 2, 3, 4, 5, 6, 7, 8)
        assert s.get_uncal_reading(2) == 60
        assert s.get_uncal_all() == (11, 12, 13, 14, 15, 16, 17, 18)
        assert mdigital.mock_calls == [
            # TODO: get rid of ord, adapt format.
            call.write_value("command", (ord("W"),)),
            call.read_value("steering"),
            call.read_value("average"),
            call.read_value("result"),
            call.write_value("set_point", (50,)),
            call.write_value("kp", (35,)),
            call.write_value("ki_divisor", (10,)),
            call.read_value("calibrated_reading_byte1"),
            call.read_value("all_calibrated_readings"),
            call.read_value("uncal_sensor2_voltage_byte1"),
            call.read_value("all_uncal_readings"),
        ]

    def test_servo(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.mindsensors.Servo, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.Servo, False)
        # TODO: command can not work, can not fit two bytes in one byte.
        mdigital.read_value.side_effect = [(1,), (42,), (43,)]
        assert s.get_bat_level() == 1
        s.set_position(1, 42)
        assert s.get_position(1) == 42
        s.set_speed(2, 43)
        assert s.get_speed(2) == 43
        s.set_quick(3, 44)
        assert mdigital.mock_calls == [
            call.read_value("command"),
            call.write_value("servo_1_pos", (42,)),
            call.read_value("servo_1_pos"),
            call.write_value("servo_2_speed", (43,)),
            call.read_value("servo_2_speed"),
            call.write_value("servo_3_quick", (44,)),
        ]

    def test_mmx(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.mindsensors.MMX, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.MMX, False)
        mdigital.read_value.side_effect = [
            (1,),
            (0xAA,),
            (0x55,),
            (12345,),
            (0x55,),
            (42,),
        ]
        # TODO: get rid of ord, adapt format.
        s.command(s.Commands.RESET_PARAMS_ENCODERS)
        assert s.get_bat_level() == 1
        s.set_encoder_target(1, 12345)
        s.set_speed(2, 50)
        s.set_time_run(1, 60)
        s.command_b(1, 42)
        s.command_a(2, 2, 1)
        s.command_a(2, 2, 0)
        assert s.get_encoder_pos(1) == 12345
        # TODO: should be bool.
        assert s.get_motor_status(1, 2) == 1
        assert s.get_tasks(1) == 42
        s.set_pid("p", "speed", 3)
        s.set_pass_count(43)
        s.set_tolerance(44)
        assert mdigital.mock_calls == [
            call.write_value("command", (ord("R"),)),
            call.read_value("command"),
            call.write_value("encoder_1_target", (12345,)),
            call.write_value("speed_2", (50,)),
            call.write_value("seconds_to_run_1", (60,)),
            call.write_value("command_b_1", (42,)),
            call.read_value("command_a_2"),
            call.write_value("command_a_2", (0xAE,)),
            call.read_value("command_a_2"),
            call.write_value("command_a_2", (0x51,)),
            call.read_value("encoder_1_pos"),
            call.read_value("status_m1"),
            call.read_value("tasks_running_m1"),
            call.write_value("p_speed", (3,)),
            call.write_value("pass_count", (43,)),
            call.write_value("tolerance", (44,)),
        ]

    def test_hid(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.mindsensors.HID, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.HID, False)
        s.command(s.Commands.ASCII_MODE)
        s.set_modifier(42)
        s.write_data("a")
        assert mdigital.mock_calls == [
            call.write_value("command", (ord("A"),)),
            call.write_value("modifier", (42,)),
            call.write_value("keyboard_data", (ord("a"),)),
        ]

    def test_ps2(self, mbrick, mdigital):
        s = mbrick.get_sensor(Port.S1, nxt.sensor.mindsensors.PS2, False)
        mdigital.read_value.side_effect = [
            (42,),
            (0x55,),
            # TODO: read everything in one read.
            (0x55,),
            (0x55,),
            (42,),
            (43,),
            (44,),
            (45,),
        ]
        s.command(s.Commands.POWER_ON)
        assert s.get_joystick("x", "left") == 42
        assert s.get_buttons(1) == 0x55
        st = s.get_sample()
        assert st.leftstick == (42, 43)
        assert st.rightstick == (44, 45)
        assert st.buttons.left is True
        assert st.buttons.down is False
        assert st.buttons.right is True
        assert st.buttons.up is False
        assert st.buttons.square is True
        assert st.buttons.cross is False
        assert st.buttons.circle is True
        assert st.buttons.triangle is False
        assert st.buttons.r1 is True
        assert st.buttons.r2 is True
        assert st.buttons.r3 is False
        assert st.buttons.l1 is False
        assert st.buttons.l2 is False
        assert st.buttons.l3 is True
        assert mdigital.mock_calls == [
            call.write_value("command", (ord("E"),)),
            call.read_value("x_left_joystick"),
            call.read_value("button_set_1"),
            call.read_value("button_set_1"),
            call.read_value("button_set_2"),
            call.read_value("x_left_joystick"),
            call.read_value("y_left_joystick"),
            call.read_value("x_right_joystick"),
            call.read_value("y_right_joystick"),
        ]


class TestHitechnic:
    """Test HiTechnic sensors."""

    def test_compass(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.Compass.get_sample
            is nxt.sensor.hitechnic.Compass.get_heading
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Compass, False)
        mdigital.read_value.return_value = (10,)
        assert s.get_heading() == 30
        assert s.get_relative_heading(0) == 30
        assert s.get_relative_heading(-170) == -160
        mdigital.read_value.return_value = (-10,)
        assert s.get_relative_heading(170) == 160
        assert s.is_in_range(-40, -20) is True
        assert s.is_in_range(-20, -40) is False
        mdigital.read_value.return_value = (0x02,)
        assert s.get_mode() == s.Modes.CALIBRATION_FAILED
        s.set_mode(s.Modes.CALIBRATION)
        with pytest.raises(ValueError):
            s.set_mode(s.Modes.CALIBRATION_FAILED)
        assert mdigital.mock_calls == [
            call.read_value("heading"),
            call.read_value("adder"),
        ] * 6 + [
            call.read_value("mode"),
            call.write_value("mode", (0x43,)),
        ]

    def test_accelerometer(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.Accelerometer.get_sample
            is nxt.sensor.hitechnic.Accelerometer.get_acceleration
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Accelerometer, False)
        mdigital.read_value.return_value = (0x12, 0x23, -0x32, 0x3, 0x0, 0x2)
        v = s.get_acceleration()
        assert (v.x, v.y, v.z) == (75, 140, -198)
        assert mdigital.mock_calls == [
            call.read_value("all_data"),
        ]

    def test_irreceiver(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.IRReceiver.get_sample
            is nxt.sensor.hitechnic.IRReceiver.get_speeds
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.IRReceiver, False)
        mdigital.read_value.return_value = (0, -16, 30, -44, 58, -72, 100, -128)
        v = s.get_speeds()
        assert (v.m1A, v.m1B) == (0, -16)
        assert v.channel_1 == (0, -16)
        assert (v.m2A, v.m2B) == (30, -44)
        assert v.channel_2 == (30, -44)
        assert (v.m3A, v.m3B) == (58, -72)
        assert v.channel_3 == (58, -72)
        # TODO: handle -128 specially.
        assert (v.m4A, v.m4B) == (100, -128)
        assert v.channel_4 == (100, -128)
        assert mdigital.mock_calls == [
            call.read_value("all_data"),
        ]

    def test_irseekerv2(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.IRSeekerv2.get_sample
            is nxt.sensor.hitechnic.IRSeekerv2.get_ac_values
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.IRSeekerv2, False)
        mdigital.read_value.side_effect = [
            (5, 42, 43, 44, 45, 46, 44),
            (5, 42, 43, 44, 45, 46),
            (0,),
        ]
        v = s.get_dc_values()
        assert v.direction == 5
        # TODO: use a tuple.
        assert v.sensor_1 == 42
        assert v.sensor_2 == 43
        assert v.sensor_3 == 44
        assert v.sensor_4 == 45
        assert v.sensor_5 == 46
        assert v.sensor_mean == 44
        assert v.get_dir_brightness(5) == 44
        assert v.get_dir_brightness(4) == 43.5
        v = s.get_ac_values()
        assert v.direction == 5
        assert v.sensor_1 == 42
        assert v.sensor_2 == 43
        assert v.sensor_3 == 44
        assert v.sensor_4 == 45
        assert v.sensor_5 == 46
        assert v.get_dir_brightness(5) == 44
        assert v.get_dir_brightness(4) == 43.5
        assert s.get_dsp_mode() == s.DSPModes.AC_DSP_1200Hz
        s.set_dsp_mode(s.DSPModes.AC_DSP_600Hz)
        assert mdigital.mock_calls == [
            call.read_value("all_DC"),
            call.read_value("all_AC"),
            call.read_value("dspmode"),
            call.write_value("dspmode", (1,)),
        ]

    def test_eopd(self, mbrick):
        assert (
            nxt.sensor.hitechnic.EOPD.get_sample
            is nxt.sensor.hitechnic.EOPD.get_scaled_value
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.EOPD)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 523, 0, 0, 0),
            (Port.S1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 398, 0, 0, 0),
            (Port.S1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 398, 0, 0, 0),
            (Port.S1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 1023, 0, 0, 0),
        ]
        # TODO: choose a mode in constructor, or raise error if no mode chosen.
        s.set_range_long()
        s.set_range_short()
        assert s.get_raw_value() == 500
        assert s.get_processed_value() == 25
        assert s.get_scaled_value() == 10
        assert s.get_scaled_value() == 250
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.LIGHT_ACTIVE, Mode.RAW),
            call.set_input_mode(Port.S1, Type.LIGHT_INACTIVE, Mode.RAW),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
        ]

    def test_colorv2(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.Colorv2.get_sample
            is nxt.sensor.hitechnic.Colorv2.get_active_color
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Colorv2, False)
        mdigital.read_value.side_effect = [
            (8, 100, 50, 0, 75, 42, 66, 33, 0),
            (100, 50, 0, 75),
            (0,),
        ]
        v = s.get_active_color()
        assert v.number == 8
        assert v.red == 100
        assert v.green == 50
        assert v.blue == 0
        assert v.white == 75
        assert v.index == 42
        assert v.normred == 66
        assert v.normgreen == 33
        assert v.normblue == 0
        v = s.get_passive_color()
        assert v.red == 100
        assert v.green == 50
        assert v.blue == 0
        assert v.white == 75
        assert s.get_mode() == s.Modes.ACTIVE
        s.set_mode(s.Modes.PASSIVE)
        assert mdigital.mock_calls == [
            call.read_value("all_data"),
            call.read_value("all_raw_data"),
            call.read_value("mode"),
            call.write_value("mode", (1,)),
        ]

    def test_giro(self, mbrick):
        assert (
            nxt.sensor.hitechnic.Gyro.get_sample
            is nxt.sensor.hitechnic.Gyro.get_rotation_speed
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Gyro)
        mbrick.get_input_values.side_effect = [
            (Port.S1, True, False, Type.ANGLE, Mode.RAW, 0, 0, 42, 0),
            (Port.S1, True, False, Type.ANGLE, Mode.RAW, 0, 0, 42, 0),
            (Port.S1, True, False, Type.ANGLE, Mode.RAW, 0, 0, 54, 0),
            (Port.S1, True, False, Type.ANGLE, Mode.RAW, 0, 0, 54, 0),
        ]
        assert s.get_rotation_speed() == 42
        s.calibrate()
        assert s.get_rotation_speed() == 12
        s.set_zero(0)
        assert s.get_rotation_speed() == 54
        assert mbrick.mock_calls == [
            call.set_input_mode(Port.S1, Type.ANGLE, Mode.RAW),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
            call.get_input_values(Port.S1),
        ]

    def test_prototype(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.hitechnic.Prototype, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Prototype, False)
        mdigital.read_value.side_effect = [
            (42, 43, 44, 45, 46),
            (0x2A,),
        ]
        v = s.get_analog()
        assert v.a0 == 42
        assert v.a1 == 43
        assert v.a2 == 44
        assert v.a3 == 45
        assert v.a4 == 46
        v = s.get_digital()
        assert v.dataint == 0x2A
        assert v.datalst == [False, True, False, True, False, True]
        assert list(v) == [False, True, False, True, False, True]
        assert v[0] is False
        assert v.d0 is False
        assert v.d1 is True
        assert v.d2 is False
        assert v.d3 is True
        assert v.d4 is False
        assert v.d5 is True
        s.set_digital(s.Digital_Data(0x15))
        s.set_digital_modes(s.Digital_Data((False, True, False, True, False, True)))
        assert mdigital.mock_calls == [
            call.read_value("all_analog"),
            call.read_value("digital_in"),
            call.write_value("digital_out", (0x15,)),
            call.write_value("digital_cont", (0x2A,)),
        ]

    def test_servocon(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.hitechnic.ServoCon, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.ServoCon, False)
        mdigital.read_value.side_effect = [
            (1,),
            (43,),
        ]
        assert s.get_status() == s.Status.RUNNING
        s.set_step_time(5)
        s.set_pos(1, 42)
        assert s.get_pwm() == 43
        s.set_pwm(44)
        assert mdigital.mock_calls == [
            call.read_value("status"),
            call.write_value("steptime", (5,)),
            call.write_value("s1pos", (42,)),
            call.read_value("pwm"),
            call.write_value("pwm", (44,)),
        ]

    def test_motorcon(self, mbrick, mdigital):
        assert not hasattr(nxt.sensor.hitechnic.MotorCon, "get_sample")
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.MotorCon, False)
        mdigital.read_value.side_effect = [
            (123456,),
            (654321,),
            (0x55,),
            (43,),
            (1,),
            (3, 2, 1),
            (0x70, 0x2),
        ]
        s.set_enc_target(1, 123456)
        assert s.get_enc_target(1) == 123456
        assert s.get_enc_current(2) == 654321
        s.set_mode(1, 0x55)
        assert s.get_mode(2) == 0x55
        s.set_power(1, 42)
        assert s.get_power(2) == 43
        s.set_gear_ratio(1, 2)
        assert s.get_gear_ratio(2) == 1
        s.set_pid(1, s.PID_Data(3, 2, 1))
        v = s.get_pid(2)
        assert (v.p, v.i, v.d) == (3, 2, 1)
        assert s.get_battery_voltage() == 450
        assert mdigital.mock_calls == [
            call.write_value("m1enctarget", (123456,)),
            call.read_value("m1enctarget"),
            call.read_value("m2enccurrent"),
            call.write_value("m1mode", (0x55,)),
            call.read_value("m2mode"),
            call.write_value("m1power", (42,)),
            call.read_value("m2power"),
            call.write_value("m1gearratio", (2,)),
            call.read_value("m2gearratio"),
            call.write_value("m1pid", (3, 2, 1)),
            call.read_value("m2pid"),
            call.read_value("batteryvoltage"),
        ]

    def test_angle(self, mbrick, mdigital):
        assert (
            nxt.sensor.hitechnic.Angle.get_sample
            is nxt.sensor.hitechnic.Angle.get_angle
        )
        s = mbrick.get_sensor(Port.S1, nxt.sensor.hitechnic.Angle, False)
        mdigital.read_value.side_effect = [
            (21, 1),
            (123456789,),
            (16,),
        ]
        assert s.get_angle() == 43
        assert s.get_accumulated_angle() == 123456789
        assert s.get_rpm() == 16
        s.calibrate()
        s.reset()
        assert mdigital.mock_calls == [
            call.read_value("angle"),
            call.read_value("angle_acc"),
            call.read_value("rpm"),
            call.write_value("mode", b"C"),
            call.write_value("mode", b"R"),
        ]
