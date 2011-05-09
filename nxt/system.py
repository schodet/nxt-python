# nxt.system module -- LEGO Mindstorms NXT system telegrams
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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
    from telegram import Telegram
    return Telegram(False, opcode)

def _create_with_file(opcode, fname):
    tgram = _create(opcode)
    tgram.add_filename(fname)
    return tgram

def _create_with_handle(opcode, handle):
    tgram = _create(opcode)
    tgram.add_u8(handle)
    return tgram

def open_read(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_open_read(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    n_bytes = tgram.parse_u32()
    return (handle, n_bytes)

def open_write(opcode, fname, n_bytes):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(n_bytes)
    return tgram

def _parse_open_write(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    return handle

def read(opcode, handle, n_bytes):
    tgram = _create_with_handle(opcode, handle)
    tgram.add_u16(n_bytes)
    return tgram

def _parse_read(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    n_bytes = tgram.parse_u16()
    data = tgram.parse_string()
    return (handle, n_bytes, data)

def write(opcode, handle, data):
    tgram = _create_with_handle(opcode, handle)
    tgram.add_string(len(data), data)
    return tgram

def _parse_write(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    n_bytes = tgram.parse_u16()
    return (handle, n_bytes)

def close(opcode, handle):
    return _create_with_handle(opcode, handle)

def _parse_close(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    return handle

def delete(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_delete(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    fname = tgram.parse_string()
    return (handle, fname)

def find_first(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_find(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    fname = tgram.parse_string(20)
    n_bytes = tgram.parse_u32()
    return (handle, fname, n_bytes)

def find_next(opcode, handle):
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

def open_write_linear(opcode, fname, n_bytes):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(n_bytes)
    return tgram

def open_read_linear(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_open_read_linear(tgram):
    tgram.check_status()
    n_bytes = tgram.parse_u32()
    return n_bytes

def open_write_data(opcode, fname, n_bytes):
    tgram = _create_with_file(opcode, fname)
    tgram.add_u32(n_bytes)
    return tgram

def open_append_data(opcode, fname):
    return _create_with_file(opcode, fname)

def _parse_open_append_data(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    n_bytes = tgram.parse_u32()
    return (handle, n_bytes)

def request_first_module(opcode, mname):
    return _create_with_file(opcode, mname)

def _parse_request_module(tgram):
    tgram.check_status()
    handle = tgram.parse_u8()
    mname = tgram.parse_string(20)
    mod_id = tgram.parse_u32()
    mod_size = tgram.parse_u32()
    mod_iomap_size = tgram.parse_u16()
    return (handle, mname, mod_id, mod_size, mod_iomap_size)

def request_next_module(opcode, handle):
    return _create_with_handle(opcode, handle)

def close_module_handle(opcode, handle):
    return _create_with_handle(opcode, handle)

def read_io_map(opcode, mod_id, offset, n_bytes):
    tgram = _create(opcode)
    tgram.add_u32(mod_id)
    tgram.add_u16(offset)
    tgram.add_u16(n_bytes)
    return tgram

def _parse_read_io_map(tgram):
    tgram.check_status()
    mod_id = tgram.parse_u32()
    n_bytes = tgram.parse_u16()
    contents = tgram.parse_string()
    return (mod_id, n_bytes, contents)

def write_io_map(opcode, mod_id, offset, content):
    tgram = _create(opcode)
    tgram.add_u32(mod_id)
    tgram.add_u16(offset)
    tgram.add_u16(len(content))
    tgram.add_string(len(content), content)
    return tgram

def _parse_write_io_map(tgram):
    tgram.check_status()
    mod_id = tgram.parse_u32()
    n_bytes = tgram.parse_u16()
    return (mod_id, n_bytes)

def boot(opcode):
    # Note: this command is USB only (no Bluetooth)
    tgram = _create(opcode)
    tgram.add_string(19, "Let's dance: SAMBA\0")
    return tgram

def _parse_boot(tgram):
    tgram.check_status()
    resp = tgram.parse_string()
    # Resp should be 'Yes\0'
    return resp

def set_brick_name(opcode, bname):
    tgram = _create(opcode)
    if len(bname) > 15:
        print "Warning! Brick name %s will be truncated to %s!" % (bname, bname[0:15])
        bname = bname[0:15]
    elif len(bname) < 15:
        bname += '\x00' * (15-len(bname)) #fill the extra chars with nulls
    tgram.add_string(len(bname), bname)
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
    a6 = tgram.parse_u8()
    # FIXME: what is a6 for?
    address = '%02X:%02X:%02X:%02X:%02X:%02X' % (a0, a1, a2, a3, a4, a5)
    signal_strength = tgram.parse_u32()
    user_flash = tgram.parse_u32()
    return (name, address, signal_strength, user_flash)

def delete_user_flash(opcode):
    return _create(opcode)

def _parse_delete_user_flash(tgram):
    tgram.check_status()

def poll_command_length(opcode, buf_num):
    tgram = _create(opcode)
    tgram.add_u8(buf_num)
    return tgram

def _parse_poll_command_length(tgram):
    buf_num = tgram.parse_u8()
    tgram.check_status()
    n_bytes = tgram.parse_u8()
    return (buf_num, n_bytes)

def poll_command(opcode, buf_num, n_bytes):
    tgram = _create(opcode)
    tgram.add_u8(buf_num)
    tgram.add_u8(n_bytes)
    return tgram

def _parse_poll_command(tgram):
    buf_num = tgram.parse_u8()
    tgram.check_status()
    n_bytes = tgram.parse_u8()
    command = tgram.parse_string()
    return (buf_num, n_bytes, command)

def bluetooth_factory_reset(opcode):
    # Note: this command is USB only (no Bluetooth)
    return _create(opcode)

def _parse_bluetooth_factory_reset(tgram):
    tgram.check_status()

#TODO Add docstrings to all methods

OPCODES = {
    0x80: (open_read, _parse_open_read),
    0x81: (open_write, _parse_open_write),
    0x82: (read, _parse_read),
    0x83: (write, _parse_write),
    0x84: (close, _parse_close),
    0x85: (delete, _parse_delete),
    0x86: (find_first, _parse_find),
    0x87: (find_next, _parse_find),
    0x88: (get_firmware_version, _parse_get_firmware_version),
    0x89: (open_write_linear, _parse_open_write),
    0x8A: (open_read_linear, _parse_open_read_linear),
    0x8B: (open_write_data, _parse_open_write),
    0x8C: (open_append_data, _parse_open_append_data),
    0x90: (request_first_module, _parse_request_module),
    0x91: (request_next_module, _parse_request_module),
    0x92: (close_module_handle, _parse_close),
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
