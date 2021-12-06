# nxt.system module -- LEGO Mindstorms NXT system telegrams
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

'Use for communications regarding the NXT filesystem and such ***ADVANCED USERS ONLY***'

def _create(opcode):
    'Create a simple system telegram'
    from .telegram import Telegram
    return Telegram(False, opcode)

def _create_with_file(opcode, fname):
    tgram = _create(opcode)
    tgram.add_filename(fname)
    return tgram

def _create_with_handle(opcode, handle):
    tgram = _create(opcode)
    tgram.add_u8(handle)
    return tgram

def file_open_read(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_file_open_read(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    size = tgram.parse_u32()
    return (handle, size)

def file_open_write(opcode, fname, size):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(size)
    return tgram

def _parse_file_open_write(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    return handle

def file_read(opcode, handle, size):
    tgram = _create_with_handle(opcode, handle)
    tgram.add_u16(size)
    return tgram

def _parse_file_read(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    size = tgram.parse_u16()
    data = tgram.parse_bytes(size)
    return (handle, data)

def file_write(opcode, handle, data):
    tgram = _create_with_handle(opcode, handle)
    tgram.add_bytes(data)
    return tgram

def _parse_file_write(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    size = tgram.parse_u16()
    return (handle, size)

def file_close(opcode, handle):
    return _create_with_handle(opcode, handle)

def _parse_file_close(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    return handle

def file_delete(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_file_delete(tgram):
    tgram.check_status()
    fname = tgram.parse_filename()
    return fname

def file_find_first(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_file_find(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    fname = tgram.parse_filename()
    size = tgram.parse_u32()
    return (handle, fname, size)

def file_find_next(opcode, handle):
    return _create_with_handle(opcode, handle)

def get_firmware_version(opcode):
    return _create(opcode)

def _parse_get_firmware_version(tgram):
    tgram.check_status()
    prot_minor = tgram.parse_u8()
    prot_major = tgram.parse_u8()
    prot_version = (prot_major, prot_minor)
    fw_minor = tgram.parse_u8()
    fw_major = tgram.parse_u8()
    fw_version = (fw_major, fw_minor)
    return (prot_version, fw_version)

def file_open_write_linear(opcode, fname, size):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(size)
    return tgram

def file_open_write_data(opcode, fname, size):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(size)
    return tgram

def file_open_append_data(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_file_open_append_data(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    available_size = tgram.parse_u32()
    return (handle, available_size)

def module_find_first(opcode, mname):
    return _create_with_file(opcode, mname)

def _parse_module_find(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    mname = tgram.parse_filename()
    mod_id = tgram.parse_u32()
    mod_size = tgram.parse_u32()
    mod_iomap_size = tgram.parse_u16()
    return (handle, mname, mod_id, mod_size, mod_iomap_size)

def module_find_next(opcode, handle):
    return _create_with_handle(opcode, handle)

def module_close(opcode, handle):
    return _create_with_handle(opcode, handle)

def _parse_module_close(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    return handle

def read_io_map(opcode, mod_id, offset, size):
    tgram = _create(opcode)
    tgram.add_u32(mod_id)
    tgram.add_u16(offset)
    tgram.add_u16(size)
    return tgram

def _parse_read_io_map(tgram):
    tgram.check_status()
    mod_id = tgram.parse_u32()
    size = tgram.parse_u16()
    contents = tgram.parse_bytes(size)
    return (mod_id, contents)

def write_io_map(opcode, mod_id, offset, content):
    tgram = _create(opcode)
    tgram.add_u32(mod_id)
    tgram.add_u16(offset)
    tgram.add_u16(len(content))
    tgram.add_bytes(content)
    return tgram

def _parse_write_io_map(tgram):
    tgram.check_status()
    mod_id = tgram.parse_u32()
    size = tgram.parse_u16()
    return (mod_id, size)

def boot(opcode):
    # Note: this command is USB only (no Bluetooth)
    tgram = _create(opcode)
    tgram.add_bytes(b"Let's dance: SAMBA\0")
    return tgram

def _parse_boot(tgram):
    tgram.check_status()
    resp = tgram.parse_bytes()
    # Resp should be 'Yes\0'
    return resp

def set_brick_name(opcode, bname):
    tgram = _create(opcode)
    tgram.add_string(15, bname)
    return tgram

def _parse_set_brick_name(tgram):
    tgram.check_status()

def get_device_info(opcode):
    return _create(opcode)

def _parse_get_device_info(tgram):
    tgram.check_status()
    name = tgram.parse_string(15)
    a0 = tgram.parse_u8()
    a1 = tgram.parse_u8()
    a2 = tgram.parse_u8()
    a3 = tgram.parse_u8()
    a4 = tgram.parse_u8()
    a5 = tgram.parse_u8()
    # a6 is not used, should be zero.
    a6 = tgram.parse_u8()
    address = '%02X:%02X:%02X:%02X:%02X:%02X' % (a0, a1, a2, a3, a4, a5)
    signal_strengths = (
        tgram.parse_u8(),
        tgram.parse_u8(),
        tgram.parse_u8(),
        tgram.parse_u8(),
    )
    user_flash = tgram.parse_u32()
    return (name, address, signal_strengths, user_flash)

def delete_user_flash(opcode):
    return _create(opcode)

def _parse_delete_user_flash(tgram):
    tgram.check_status()

def poll_command_length(opcode, buf_num):
    tgram = _create(opcode)
    tgram.add_u8(buf_num)
    return tgram

def _parse_poll_command_length(tgram):
    tgram.check_status()
    buf_num = tgram.parse_u8()
    size = tgram.parse_u8()
    return (buf_num, size)

def poll_command(opcode, buf_num, size):
    tgram = _create(opcode)
    tgram.add_u8(buf_num)
    tgram.add_u8(size)
    return tgram

def _parse_poll_command(tgram):
    tgram.check_status()
    buf_num = tgram.parse_u8()
    size = tgram.parse_u8()
    command = tgram.parse_bytes(size)
    return (buf_num, command)

def bluetooth_factory_reset(opcode):
    # Note: this command is USB only (no Bluetooth)
    return _create(opcode)

def _parse_bluetooth_factory_reset(tgram):
    tgram.check_status()

#TODO Add docstrings to all methods

OPCODES = {
    0x80: (file_open_read, _parse_file_open_read),
    0x81: (file_open_write, _parse_file_open_write),
    0x82: (file_read, _parse_file_read),
    0x83: (file_write, _parse_file_write),
    0x84: (file_close, _parse_file_close),
    0x85: (file_delete, _parse_file_delete),
    0x86: (file_find_first, _parse_file_find),
    0x87: (file_find_next, _parse_file_find),
    0x88: (get_firmware_version, _parse_get_firmware_version),
    0x89: (file_open_write_linear, _parse_file_open_write),
    0x8B: (file_open_write_data, _parse_file_open_write),
    0x8C: (file_open_append_data, _parse_file_open_append_data),
    0x90: (module_find_first, _parse_module_find),
    0x91: (module_find_next, _parse_module_find),
    0x92: (module_close, _parse_module_close),
    0x94: (read_io_map, _parse_read_io_map),
    0x95: (write_io_map, _parse_write_io_map),
    0x97: (boot, _parse_boot),
    0x98: (set_brick_name, _parse_set_brick_name),
    0x9B: (get_device_info, _parse_get_device_info),
    0xA0: (delete_user_flash, _parse_delete_user_flash),
    0xA1: (poll_command_length, _parse_poll_command_length),
    0xA2: (poll_command, _parse_poll_command),
    0xA4: (bluetooth_factory_reset, _parse_bluetooth_factory_reset),
}
