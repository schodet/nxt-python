# test_brick -- Test nxt.brick module
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
from unittest.mock import Mock, call, patch

import pytest

import nxt.brick
import nxt.error
import nxt.motor


@pytest.fixture
def sock():
    return Mock(spec_set=("send", "recv", "close"))


@pytest.fixture
def brick(sock):
    """A brick with a mock socket."""
    return nxt.brick.Brick(sock)


def sent(sent):
    return [call.send(sent)]


def sent_recved(sent):
    return [call.send(sent), call.recv()]


test_rxe_bin = b"test.rxe\0\0\0\0\0\0\0\0\0\0\0\0"
test_rso_bin = b"test.rso\0\0\0\0\0\0\0\0\0\0\0\0"
star_star_bin = b"*.*\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
loader_bin = b"Loader\0\0\0\0\0\0\0\0\0\0\0\0\0\0"


def test_close(sock, brick):
    brick.close()
    assert sock.mock_calls == [call.close()]


def test_with(sock, brick):
    with brick:
        pass
    assert sock.mock_calls == [call.close()]


def test_reply_error(sock, brick):
    sock.recv.return_value = bytes.fromhex("019700") + b"No\0"
    with pytest.raises(nxt.error.ProtocolError):
        brick.boot(sure=True)
    sock.recv.return_value = bytes.fromhex("029900") + b"No\0"
    with pytest.raises(nxt.error.ProtocolError):
        brick.boot(sure=True)
    sock.recv.return_value = bytes.fromhex("029799") + b"No\0"
    with pytest.raises(nxt.error.ProtocolError):
        brick.boot(sure=True)


class TestSystem:
    """Test system commands."""

    def test_file_open_read(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028000 42 01020304")
        handle, size = brick.file_open_read("test.rxe")
        assert sock.mock_calls == sent_recved(bytes.fromhex("0180") + test_rxe_bin)
        assert handle == 0x42
        assert size == 0x04030201

    def test_file_open_read_fail(self, sock, brick):
        """Test command failure reported in status code."""
        sock.recv.return_value = bytes.fromhex("028087 00 00000000")
        with pytest.raises(nxt.error.FileNotFoundError):
            brick.file_open_read("unknown.rxe")

    def test_file_open_write(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028100 42")
        handle = brick.file_open_write("test.rxe", 0x04030201)
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0181") + test_rxe_bin + bytes.fromhex("01020304")
        )
        assert handle == 0x42

    def test_file_read(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028200 42 0700 21222324252627")
        handle, data = brick.file_read(0x42, 7)
        # TODO: The file_read command will return a EOF error if end of file is reached
        # before the read can be finished, and size will still contain the requested
        # data length instead of the actual read length. This is not the classic
        # semantic of a Unix read. Avoid reading past the end of file.
        assert sock.mock_calls == sent_recved(bytes.fromhex("0182 42 0700"))
        assert handle == 0x42
        assert data == bytes.fromhex("21222324252627")

    def test_file_write(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028300 42 0700")
        handle, size = brick.file_write(0x42, bytes.fromhex("21222324252627"))
        assert sock.mock_calls == sent_recved(bytes.fromhex("0183 42 21222324252627"))
        assert handle == 0x42
        assert size == 7

    def test_file_close(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028400 42")
        handle = brick.file_close(0x42)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0184 42"))
        assert handle == 0x42

    def test_file_delete(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("028500") + b"test.rxe\0\0\0\0\0\0\0\0\0\0\0\0"
        )
        name = brick.file_delete("test.rxe")
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0185") + b"test.rxe\0\0\0\0\0\0\0\0\0\0\0\0"
        )
        assert name == "test.rxe"

    def test_file_find_first(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("028600 42") + test_rxe_bin + bytes.fromhex("01020304")
        )
        handle, name, size = brick.file_find_first("*.*")
        assert sock.mock_calls == sent_recved(bytes.fromhex("0186") + star_star_bin)
        assert handle == 0x42
        assert name == "test.rxe"
        assert size == 0x04030201

    def test_file_find_next(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("028700 42") + test_rxe_bin + bytes.fromhex("01020304")
        )
        handle, name, size = brick.file_find_next(0x42)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0187 42"))
        assert handle == 0x42
        assert name == "test.rxe"
        assert size == 0x04030201

    def test_get_firmware_version(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028800 0102 0304")
        prot_version, fw_version = brick.get_firmware_version()
        assert sock.mock_calls == sent_recved(bytes.fromhex("0188"))
        assert prot_version == (2, 1)
        assert fw_version == (4, 3)

    def test_file_open_write_linear(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028900 42")
        handle = brick.file_open_write_linear("test.rxe", 0x04030201)
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0189") + test_rxe_bin + bytes.fromhex("01020304")
        )
        assert handle == 0x42

    def test_file_open_write_data(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028b00 42")
        handle = brick.file_open_write_data("test.rxe", 0x04030201)
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("018b") + test_rxe_bin + bytes.fromhex("01020304")
        )
        assert handle == 0x42

    def test_file_open_append_data(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("028c00 42 01020304")
        handle, available_size = brick.file_open_append_data("test.rxe")
        assert sock.mock_calls == sent_recved(bytes.fromhex("018c") + test_rxe_bin)
        assert handle == 0x42
        assert available_size == 0x04030201

    def test_module_find_first(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("029000 42")
            + loader_bin
            + bytes.fromhex("01000900 00000000 0800")
        )
        handle, name, mod_id, mod_size, mod_iomap_size = brick.module_find_first("*.*")
        assert sock.mock_calls == sent_recved(bytes.fromhex("0190") + star_star_bin)
        assert handle == 0x42
        assert name == "Loader"
        assert mod_id == 0x00090001
        assert mod_size == 0
        assert mod_iomap_size == 8

    def test_module_find_next(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("029100 42")
            + loader_bin
            + bytes.fromhex("01000900 00000000 0800")
        )
        handle, name, mod_id, mod_size, mod_iomap_size = brick.module_find_next(0x42)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0191 42"))
        assert handle == 0x42
        assert name == "Loader"
        assert mod_id == 0x00090001
        assert mod_size == 0
        assert mod_iomap_size == 8

    def test_module_close(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("029200 42")
        handle = brick.module_close(0x42)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0192 42"))
        assert handle == 0x42

    def test_read_io_map(self, sock, brick):
        sock.recv.return_value = bytes.fromhex(
            "029400 01020304 0700 212223242526270000"
        )
        mod_id, data = brick.read_io_map(0x04030201, 0x3231, 0x4241)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0194 01020304 3132 4142"))
        assert mod_id == 0x04030201
        assert data == bytes.fromhex("21222324252627")

    def test_write_io_map(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("029500 01020304 0700")
        mod_id, size = brick.write_io_map(
            0x04030201, 0x3231, bytes.fromhex("21222324252627")
        )
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0195 01020304 3132 0700 21222324252627")
        )
        assert mod_id == 0x04030201
        assert size == 7

    def test_boot_not_sure(self, sock, brick):
        with pytest.raises(ValueError):
            brick.boot()

    def test_boot(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("029700") + b"Yes\0"
        resp = brick.boot(sure=True)
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0197") + b"Let's dance: SAMBA\0"
        )
        assert resp == b"Yes\0"

    def test_set_brick_name(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("029800")
        brick.set_brick_name("NXT")
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0198") + b"NXT\0\0\0\0\0\0\0\0\0\0\0\0"
        )

    def test_set_brick_name_too_long(self, sock, brick):
        with pytest.raises(ValueError):
            brick.set_brick_name("NXT456789012345")

    def test_get_device_info(self, sock, brick):
        sock.recv.return_value = (
            bytes.fromhex("029b00")
            + b"NXT\0\0\0\0\0\0\0\0\0\0\0\0"
            + bytes.fromhex("01020304050600" "11121314" "21222324")
        )
        name, address, signal_strengths, user_flash = brick.get_device_info()
        assert sock.mock_calls == sent_recved(bytes.fromhex("019b"))
        assert name == "NXT"
        assert address == "01:02:03:04:05:06"
        assert signal_strengths == (0x11, 0x12, 0x13, 0x14)
        assert user_flash == 0x24232221

    def test_delete_user_flash(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("02a000")
        brick.delete_user_flash()
        assert sock.mock_calls == sent_recved(bytes.fromhex("01a0"))

    def test_poll_command_length(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("02a100 01 07")
        buf_num, size = brick.poll_command_length(1)
        assert sock.mock_calls == sent_recved(bytes.fromhex("01a1 01"))
        assert buf_num == 1
        assert size == 7

    def test_poll_command(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("02a200 01 07 212223242526270000")
        buf_num, command = brick.poll_command(1, 9)
        assert sock.mock_calls == sent_recved(bytes.fromhex("01a2 01 09"))
        assert buf_num == 1
        assert command == bytes.fromhex("21222324252627")

    def test_bluetooth_factory_reset(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("02a400")
        brick.bluetooth_factory_reset()
        assert sock.mock_calls == sent_recved(bytes.fromhex("01a4"))


class TestDirect:
    """Test direct commands."""

    def test_start_program(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020000")
        brick.start_program("test.rxe")
        assert sock.mock_calls == sent_recved(bytes.fromhex("0000") + test_rxe_bin)

    def test_stop_program(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020100")
        brick.stop_program()
        assert sock.mock_calls == sent_recved(bytes.fromhex("0001"))

    def test_play_sound_file(self, sock, brick):
        brick.play_sound_file(True, "test.rso")
        assert sock.mock_calls == sent(bytes.fromhex("8002 01") + test_rso_bin)

    def test_play_tone(self, sock, brick):
        brick.play_tone(440, 1000)
        assert sock.mock_calls == sent(bytes.fromhex("8003 b801 e803"))

    def test_play_tone_and_wait(self, sock, brick):
        with patch("nxt.brick.time.sleep") as sleep:
            brick.play_tone_and_wait(440, 1000)
            assert sock.mock_calls == sent(bytes.fromhex("8003 b801 e803"))
            assert sleep.mock_calls == [call(1)]

    def test_set_output_state(self, sock, brick):
        brick.set_output_state(
            nxt.motor.Port.B,
            -100,
            nxt.motor.Mode.ON,
            nxt.motor.RegulationMode.IDLE,
            -5,
            nxt.motor.RunState.RUNNING,
            0x04030201,
        )
        assert sock.mock_calls == sent(bytes.fromhex("8004 01 9c 01 00 fb 20 01020304"))

    def test_set_input_mode(self, sock, brick):
        brick.set_input_mode(
            nxt.sensor.Port.S3, nxt.sensor.Type.SWITCH, nxt.sensor.Mode.BOOL
        )
        assert sock.mock_calls == sent(bytes.fromhex("8005 02 01 20"))

    def test_get_output_state(self, sock, brick):
        sock.recv.return_value = bytes.fromhex(
            "020600 01 9c 01 00 fb 20 01020304 11121314 21222324 31323334"
        )
        (
            port,
            power,
            mode,
            regulation_mode,
            turn_ratio,
            run_state,
            tacho_limit,
            tacho_count,
            block_tacho_count,
            rotation_count,
        ) = brick.get_output_state(nxt.motor.Port.B)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0006 01"))
        assert port == nxt.motor.Port.B
        assert power == -100
        assert mode == nxt.motor.Mode.ON
        assert regulation_mode == nxt.motor.RegulationMode.IDLE
        assert turn_ratio == -5
        assert run_state == nxt.motor.RunState.RUNNING
        assert tacho_limit == 0x04030201
        assert tacho_count == 0x14131211
        assert block_tacho_count == 0x24232221
        assert rotation_count == 0x34333231

    def test_get_input_values(self, sock, brick):
        sock.recv.return_value = bytes.fromhex(
            "020700 02 01 00 01 20 0102 1112 2122 3132"
        )
        (
            port,
            valid,
            calibrated,
            sensor_type,
            sensor_mode,
            raw_value,
            normalized_value,
            scaled_value,
            calibrated_value,
        ) = brick.get_input_values(nxt.sensor.Port.S3)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0007 02"))
        assert port == nxt.sensor.Port.S3
        assert valid is True
        assert calibrated is False
        assert sensor_type == nxt.sensor.Type.SWITCH
        assert sensor_mode == nxt.sensor.Mode.BOOL
        assert raw_value == 0x0201
        assert normalized_value == 0x1211
        assert scaled_value == 0x2221
        assert calibrated_value == 0x3231

    def test_reset_input_scaled_value(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020800")
        brick.reset_input_scaled_value(nxt.sensor.Port.S3)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0008 02"))

    def test_message_write(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020900")
        brick.message_write(3, bytes.fromhex("21222324252627"))
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("0009 03 08 21222324252627 00")
        )

    def test_message_write_too_large(self, sock, brick):
        with pytest.raises(ValueError):
            brick.message_write(3, bytes.fromhex("21") * 59)

    def test_reset_motor_position(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020a00")
        brick.reset_motor_position(nxt.motor.Port.B, True)
        assert sock.mock_calls == sent_recved(bytes.fromhex("000a 01 01"))

    def test_get_battery_level(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020b00 2823")
        millivolts = brick.get_battery_level()
        assert sock.mock_calls == sent_recved(bytes.fromhex("000b"))
        assert millivolts == 9000

    def test_stop_sound_playback(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020c00")
        brick.stop_sound_playback()
        assert sock.mock_calls == sent_recved(bytes.fromhex("000c"))

    def test_keep_alive(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020d00 01020304")
        sleep_timeout = brick.keep_alive()
        assert sock.mock_calls == sent_recved(bytes.fromhex("000d"))
        assert sleep_timeout == 0x04030201

    def test_ls_get_status(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020e00 07")
        size = brick.ls_get_status(nxt.sensor.Port.S3)
        assert sock.mock_calls == sent_recved(bytes.fromhex("000e 02"))
        assert size == 7

    def test_ls_write(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("020f00")
        brick.ls_write(nxt.sensor.Port.S3, bytes.fromhex("21222324252627"), 9)
        assert sock.mock_calls == sent_recved(
            bytes.fromhex("000f 02 07 09 21222324252627")
        )

    def test_ls_read(self, sock, brick):
        sock.recv.return_value = bytes.fromhex(
            "021000 07 21222324252627 000000000000000000"
        )
        rx_data = brick.ls_read(nxt.sensor.Port.S3)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0010 02"))
        assert rx_data == bytes.fromhex("21222324252627")

    def test_get_current_program_name(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("021100") + test_rxe_bin
        name = brick.get_current_program_name()
        assert sock.mock_calls == sent_recved(bytes.fromhex("0011"))
        assert name == "test.rxe"

    def test_message_read(self, sock, brick):
        sock.recv.return_value = bytes.fromhex("021300 00 07 21222324252627") + bytes(
            52
        )
        local_inbox, message = brick.message_read(10, 0, True)
        assert sock.mock_calls == sent_recved(bytes.fromhex("0013 0a 00 01"))
        assert local_inbox == 0
        assert message == bytes.fromhex("21222324252627")


class TestFilesModules:
    """Test nxt.brick files & modules access."""

    def test_find_files_none(self, mbrick):
        mbrick.file_find_first.side_effect = [nxt.error.FileNotFoundError()]
        results = list(mbrick.find_files("*.*"))
        assert results == []
        assert mbrick.mock_calls == [
            call.file_find_first("*.*"),
        ]

    def test_find_files_one(self, mbrick):
        mbrick.file_find_first.return_value = (0x42, "test.rxe", 0x04030201)
        mbrick.file_find_next.side_effect = [nxt.error.FileNotFoundError()]
        results = list(mbrick.find_files("*.*"))
        assert results == [("test.rxe", 0x04030201)]
        assert mbrick.mock_calls == [
            call.file_find_first("*.*"),
            call.file_find_next(0x42),
            call.file_close(0x42),
        ]

    def test_find_files_two(self, mbrick):
        mbrick.file_find_first.return_value = (0x42, "test.rxe", 0x04030201)
        mbrick.file_find_next.side_effect = [
            (0x42, "test.rso", 7),
            nxt.error.FileNotFoundError(),
        ]
        results = list(mbrick.find_files("*.*"))
        assert results == [("test.rxe", 0x04030201), ("test.rso", 7)]
        assert mbrick.mock_calls == [
            call.file_find_first("*.*"),
            call.file_find_next(0x42),
            call.file_find_next(0x42),
            call.file_close(0x42),
        ]

    def test_find_files_interrupted(self, mbrick):
        mbrick.file_find_first.return_value = (0x42, "test.rxe", 0x04030201)
        mbrick.file_find_next.side_effect = [nxt.error.FileNotFoundError()]
        g = mbrick.find_files("*.*")
        assert next(g) == ("test.rxe", 0x04030201)
        g.close()
        assert mbrick.mock_calls == [
            call.file_find_first("*.*"),
            call.file_close(0x42),
        ]

    def test_find_modules_none(self, mbrick):
        mbrick.module_find_first.side_effect = [nxt.error.ModuleNotFoundError()]
        results = list(mbrick.find_modules("*.*"))
        assert results == []
        assert mbrick.mock_calls == [
            call.module_find_first("*.*"),
        ]

    def test_find_modules_one(self, mbrick):
        mbrick.module_find_first.return_value = (0x42, "Loader", 0x00090001, 0, 8)
        mbrick.module_find_next.side_effect = [nxt.error.ModuleNotFoundError()]
        results = list(mbrick.find_modules("*.*"))
        assert mbrick.mock_calls == [
            call.module_find_first("*.*"),
            call.module_find_next(0x42),
            call.module_close(0x42),
        ]
        assert results == [("Loader", 0x00090001, 0, 8)]

    def test_find_modules_two(self, mbrick):
        mbrick.module_find_first.return_value = (0x42, "Loader", 0x00090001, 0, 8)
        mbrick.module_find_next.side_effect = [
            (0x42, "Dummy", 0x01020304, 0, 12),
            nxt.error.ModuleNotFoundError(),
        ]
        results = list(mbrick.find_modules("*.*"))
        assert mbrick.mock_calls == [
            call.module_find_first("*.*"),
            call.module_find_next(0x42),
            call.module_find_next(0x42),
            call.module_close(0x42),
        ]
        assert results == [
            ("Loader", 0x00090001, 0, 8),
            ("Dummy", 0x01020304, 0, 12),
        ]

    def test_file_read_text(self, mbrick):
        mbrick.file_open_read.return_value = (0x42, 12)
        mbrick.file_read.return_value = (0x42, b"hello\nworld\n")
        with mbrick.open_file("test.txt") as f:
            results = list(f)
        assert results == ["hello\n", "world\n"]
        assert mbrick.mock_calls == [
            call.file_open_read("test.txt"),
            call.file_read(0x42, 12),
            call.file_close(0x42),
        ]

    def test_file_read_bin(self, mbrick):
        mbrick.file_open_read.return_value = (0x42, 7)
        mbrick.file_read.return_value = (0x42, bytes.fromhex("21222324252627"))
        with mbrick.open_file("test.bin", "rb") as f:
            assert f.read() == bytes.fromhex("21222324252627")
        assert mbrick.mock_calls == [
            call.file_open_read("test.bin"),
            call.file_read(0x42, 7),
            call.file_close(0x42),
        ]

    def test_file_read_raw(self, mbrick):
        mbrick.file_open_read.return_value = (0x42, 7)
        mbrick.file_read.return_value = (0x42, bytes.fromhex("21222324252627"))
        with mbrick.open_file("test.bin", "rb", buffering=0) as f:
            assert f.read() == bytes.fromhex("21222324252627")
        assert mbrick.mock_calls == [
            call.file_open_read("test.bin"),
            call.file_read(0x42, 7),
            call.file_close(0x42),
        ]

    def test_file_write_text(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 12)
        f = mbrick.open_file("test.txt", "wt", 12)
        f.write("hello\n")
        f.write("world\n")
        f.close()
        assert mbrick.mock_calls == [
            call.file_open_write("test.txt", 12),
            call.file_write(0x42, b"hello\nworld\n"),
            call.file_close(0x42),
        ]

    def test_file_write_text_encoding(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 16)
        f = mbrick.open_file("test.txt", "wt", 16, errors="replace")
        f.write("un petit café ?\n")
        f.close()
        assert mbrick.mock_calls == [
            call.file_open_write("test.txt", 16),
            call.file_write(0x42, b"un petit caf? ?\n"),
            call.file_close(0x42),
        ]

    def test_file_write_bin(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 7)
        f = mbrick.open_file("test.bin", "wb", 7)
        f.write(bytes.fromhex("21222324252627"))
        f.close()
        assert mbrick.mock_calls == [
            call.file_open_write("test.bin", 7),
            call.file_write(0x42, bytes.fromhex("21222324252627")),
            call.file_close(0x42),
        ]

    def test_file_write_raw(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 7)
        f = mbrick.open_file("test.bin", "wb", 7, buffering=0)
        f.write(bytes.fromhex("21222324252627"))
        f.close()
        assert mbrick.mock_calls == [
            call.file_open_write("test.bin", 7),
            call.file_write(0x42, bytes.fromhex("21222324252627")),
            call.file_close(0x42),
        ]

    def test_file_write_too_much(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 7)
        f = mbrick.open_file("test.bin", "wb", 7)
        f.write(bytes.fromhex("2122232425262728"))
        with pytest.raises(ValueError):
            # Flush done on close.
            f.close()
        assert f.closed
        assert mbrick.mock_calls == [
            call.file_open_write("test.bin", 7),
            call.file_write(0x42, bytes.fromhex("21222324252627")),
            call.file_close(0x42),
        ]

    def test_file_write_closed(self, mbrick):
        mbrick.file_open_write.return_value = 0x42
        mbrick.file_write.return_value = (0x42, 7)
        # Write directly to raw file to bypass error check in buffered file.
        f = mbrick.open_file("test.bin", "wb", 7, buffering=0)
        f.close()
        assert f.closed
        with pytest.raises(ValueError):
            f.write(bytes.fromhex("28"))
        assert mbrick.mock_calls == [
            call.file_open_write("test.bin", 7),
            call.file_close(0x42),
        ]

    def test_file_invalid_params(self, mbrick):
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "ww", 7)
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "wr", 7)
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "tb")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "t")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "x")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "rb", encoding="ascii")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "rb", errors="ignore")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "rb", newline="\n")
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "r", buffering=0)
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "r", 7)
        with pytest.raises(ValueError):
            mbrick.open_file("test.bin", "w")
