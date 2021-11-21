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
from unittest.mock import Mock, call

import pytest

import nxt.sensor
from nxt.sensor import PORT_1, PORT_2, Mode, Type


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
        s = nxt.sensor.analog.BaseAnalogSensor(mbrick, PORT_1)
        mbrick.get_input_values.side_effect = [
            (PORT_1, True, False, Type.SWITCH, Mode.BOOLEAN, 1, 2, 3, 4),
        ]
        s.set_input_mode(Type.SWITCH, Mode.BOOLEAN)
        v = s.get_input_values()
        assert v.port == PORT_1
        assert v.valid is True
        assert v.calibrated is False
        assert v.sensor_type == Type.SWITCH
        assert v.mode == Mode.BOOLEAN
        assert v.raw_ad_value == 1
        assert v.normalized_ad_value == 2
        assert v.scaled_value == 3
        assert v.calibrated_value == 4
        assert str(v).startswith("(")
        s.reset_input_scaled_value()
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.SWITCH, Mode.BOOLEAN),
            call.get_input_values(PORT_1),
            call.reset_input_scaled_value(PORT_1),
        ]

    def test_touch(self, mbrick):
        assert nxt.sensor.Touch.get_sample is nxt.sensor.Touch.is_pressed
        s = nxt.sensor.Touch(mbrick, PORT_1)
        mbrick.get_input_values.side_effect = [
            (PORT_1, True, False, Type.SWITCH, Mode.BOOLEAN, 1023, 1023, 0, 1023),
            (PORT_1, True, False, Type.SWITCH, Mode.BOOLEAN, 183, 183, 1, 183),
        ]
        assert s.is_pressed() is False
        assert s.is_pressed() is True
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.SWITCH, Mode.BOOLEAN),
            call.get_input_values(PORT_1),
            call.get_input_values(PORT_1),
        ]

    def test_light(self, mbrick):
        assert nxt.sensor.Light.get_sample is nxt.sensor.Light.get_lightness
        s = nxt.sensor.Light(mbrick, PORT_1)
        mbrick.get_input_values.side_effect = [
            (PORT_1, True, False, Type.LIGHT_ACTIVE, Mode.RAW, 726, 250, 250, 250),
            (PORT_1, True, False, Type.LIGHT_INACTIVE, Mode.RAW, 823, 107, 107, 107),
        ]
        assert s.get_lightness() == 250
        s.set_illuminated(False)
        assert s.get_lightness() == 107
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.LIGHT_ACTIVE, Mode.RAW),
            call.get_input_values(PORT_1),
            call.set_input_mode(PORT_1, Type.LIGHT_INACTIVE, Mode.RAW),
            call.get_input_values(PORT_1),
        ]

    def test_sound(self, mbrick):
        assert nxt.sensor.Sound.get_sample is nxt.sensor.Sound.get_loudness
        s = nxt.sensor.Sound(mbrick, PORT_1)
        mbrick.get_input_values.side_effect = [
            (PORT_1, True, False, Type.SOUND_DBA, Mode.RAW, 999, 15, 15, 15),
            (PORT_1, True, False, Type.SOUND_DB, Mode.RAW, 999, 15, 15, 15),
        ]
        assert s.get_loudness() == 15
        s.set_adjusted(False)
        assert s.get_loudness() == 15
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.SOUND_DBA, Mode.RAW),
            call.get_input_values(PORT_1),
            call.set_input_mode(PORT_1, Type.SOUND_DB, Mode.RAW),
            call.get_input_values(PORT_1),
        ]

    def test_color20(self, mbrick):
        assert nxt.sensor.Color20.get_sample is nxt.sensor.Color20.get_color
        s = nxt.sensor.Color20(mbrick, PORT_1)
        mbrick.get_input_values.side_effect = [
            (PORT_1, True, False, Type.COLORFULL, Mode.RAW, 0, 0, 4, 0),
            (PORT_1, True, False, Type.COLORFULL, Mode.RAW, 0, 0, 4, 0),
            # TODO: handle invalid measures on configuration change.
            (PORT_1, True, False, Type.COLORRED, Mode.RAW, 114, 46, 46, 46),
            (PORT_1, True, False, Type.COLORRED, Mode.RAW, 114, 46, 46, 46),
        ]
        assert s.get_color() == 4
        assert s.get_reflected_light(Type.COLORRED) == 46
        assert s.get_light_color() == Type.COLORRED
        assert mbrick.mock_calls == [
            # TODO: set too much input mode.
            call.set_input_mode(PORT_1, Type.COLORFULL, Mode.RAW),
            call.set_input_mode(PORT_1, Type.COLORFULL, Mode.RAW),
            # TODO: get too much input values.
            call.get_input_values(PORT_1),
            call.get_input_values(PORT_1),
            call.set_input_mode(PORT_1, Type.COLORRED, Mode.RAW),
            call.get_input_values(PORT_1),
            call.get_input_values(PORT_1),
        ]


@pytest.mark.usefixtures("mtime")
class TestDigital:
    """Test nxt.sensor.digital."""

    version_bin = b"V1.0\0\0\0\0"
    product_id_bin = b"LEGO\0\0\0\0"
    sensor_type_bin = b"Sonar\0\0\0"

    def test_get_sensor_info(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
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
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(PORT_1, bytes((0x02, 0x00)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            call.ls_write(PORT_1, bytes((0x02, 0x10)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
        ]

    def test_check_compatible(self, mbrick, capsys):
        class DummySensor(nxt.sensor.BaseDigitalSensor):
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
        DummySensor(mbrick, PORT_1)
        assert "WARNING" not in capsys.readouterr()[0]
        DummySensor(mbrick, PORT_2)
        assert "WARNING" in capsys.readouterr()[0]

    def test_write_value(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
        s.I2C_ADDRESS = dict(s.I2C_ADDRESS, command=(0x41, "B"))
        s.write_value("command", (0x12,))
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(PORT_1, bytes((0x02, 0x41, 0x12)), 0),
        ]

    def test_not_ready(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
        mbrick.ls_get_status.side_effect = [nxt.error.I2CPendingError("pending"), 8]
        mbrick.ls_read.return_value = self.product_id_bin
        assert s.read_value("product_id") == (self.product_id_bin,)
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
        ]

    def test_status_timeout(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
        mbrick.ls_get_status.side_effect = (
            [nxt.error.I2CPendingError("pending")] * 30 * 3
        )
        with pytest.raises(nxt.error.I2CError):
            s.read_value("product_id")
        mock_calls = [call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW)] + (
            [call.ls_write(PORT_1, bytes((0x02, 0x08)), 8)]
            + [call.ls_get_status(PORT_1)] * 30
            + [call.ls_read(PORT_1)]
        ) * 3
        assert mbrick.mock_calls == mock_calls

    def test_read_error(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
        mbrick.ls_get_status.side_effect = [8, 8]
        mbrick.ls_read.side_effect = [self.product_id_bin[1:], self.product_id_bin]
        assert s.read_value("product_id") == (self.product_id_bin,)
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            # Retry.
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
        ]

    def test_read_timeout(self, mbrick):
        s = nxt.sensor.BaseDigitalSensor(mbrick, PORT_1, False)
        mbrick.ls_get_status.return_value = 8
        mbrick.ls_read.return_value = self.product_id_bin[1:]
        with pytest.raises(nxt.error.I2CError):
            s.read_value("product_id")
        mock_calls = [call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW)] + [
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
        ] * 3
        assert mbrick.mock_calls == mock_calls

    def test_find_class(self):
        def test(info, cls):
            found = nxt.sensor.find_class(nxt.sensor.digital.SensorInfo(*info))
            assert found is cls

        test(("V1.0", "LEGO", "Sonar"), nxt.sensor.Ultrasonic)
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
        assert mbrick.get_sensor(PORT_1).__class__ is nxt.sensor.Ultrasonic
        assert mbrick.mock_calls == [
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
            call.ls_write(PORT_1, bytes((0x02, 0x00)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            call.ls_write(PORT_1, bytes((0x02, 0x08)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            call.ls_write(PORT_1, bytes((0x02, 0x10)), 8),
            call.ls_get_status(PORT_1),
            call.ls_read(PORT_1),
            call.set_input_mode(PORT_1, Type.LOW_SPEED_9V, Mode.RAW),
        ]


class TestGenericDigital:
    """Test LEGO digital sensors."""

    def test_ultrasonic(self, mbrick, mdigital):
        assert nxt.sensor.Ultrasonic.get_sample is nxt.sensor.Ultrasonic.get_distance
        s = nxt.sensor.Ultrasonic(mbrick, PORT_1, check_compatible=False)
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
        s.command(s.Commands.OFF)
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
        assert nxt.sensor.Temperature.get_sample is nxt.sensor.Temperature.get_deg_c
        s = nxt.sensor.Temperature(mbrick, PORT_1)
        mdigital.read_value.return_value = (1600 * 16,)
        assert s.get_deg_c() == 100
        assert s.get_deg_f() == 212
        assert mdigital.mock_calls == [
            call.read_value("raw_value"),
            call.read_value("raw_value"),
        ]
