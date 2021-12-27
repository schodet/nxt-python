Brick
=====

.. automodule:: nxt.brick

   .. autoclass:: Brick

   Connection Management
   ---------------------

   .. automethod:: Brick.close

   You can also use the context manager interface::

      with nxt.locator.find() as b:
          b.play_tone(440, 1000)
      # Here, connection is closed automatically.

   Brick Information
   -----------------

   .. automethod:: Brick.get_device_info
   .. automethod:: Brick.get_battery_level
   .. automethod:: Brick.get_firmware_version
   .. automethod:: Brick.set_brick_name
   .. automethod:: Brick.keep_alive

   Sound
   -----

   .. automethod:: Brick.play_tone_and_wait
   .. automethod:: Brick.play_sound_file
   .. automethod:: Brick.play_tone
   .. automethod:: Brick.stop_sound_playback

   Motors and Sensors
   ------------------

   .. automethod:: Brick.get_motor
   .. automethod:: Brick.get_sensor

   Programs
   --------

   .. automethod:: Brick.start_program
   .. automethod:: Brick.stop_program
   .. automethod:: Brick.get_current_program_name

   File System Access
   ------------------

   Brick file system has no directory and file names are not case sensitive.

   .. automethod:: Brick.open_file
   .. automethod:: Brick.find_files
   .. automethod:: Brick.file_delete
   .. automethod:: Brick.delete_user_flash

   Mailboxes
   ---------

   Mailboxes can be used to exchange messages with the running program.

   .. automethod:: Brick.message_write
   .. automethod:: Brick.message_read

   Low Level Modules Access
   ------------------------

   Low level modules access allows to read and write directly in modules
   memory. This can be used for example to take a screenshot or to debug the
   virtual machine. You need to look at the firmware source code for how to
   use it.

   .. automethod:: Brick.find_modules
   .. automethod:: Brick.read_io_map
   .. automethod:: Brick.write_io_map

   Low Level Output Ports Methods
   ------------------------------

   These are low level methods, you can use the :mod:`nxt.motor` module for an
   easier interface.

   .. automethod:: Brick.set_output_state
   .. automethod:: Brick.get_output_state
   .. automethod:: Brick.reset_motor_position

   Low Level Intput Ports Methods
   ------------------------------

   This are low level methods, you can use the :mod:`nxt.sensor` module for an
   easier interface.

   .. automethod:: Brick.set_input_mode
   .. automethod:: Brick.get_input_values
   .. automethod:: Brick.reset_input_scaled_value
   .. automethod:: Brick.ls_get_status
   .. automethod:: Brick.ls_write
   .. automethod:: Brick.ls_read

   Low Level Methods
   -----------------

   Do not use these functions unless you know exactly what you are doing.

   .. automethod:: Brick.file_open_read
   .. automethod:: Brick.file_open_write
   .. automethod:: Brick.file_read
   .. automethod:: Brick.file_write
   .. automethod:: Brick.file_close
   .. automethod:: Brick.file_find_first
   .. automethod:: Brick.file_find_next
   .. automethod:: Brick.file_open_write_linear
   .. automethod:: Brick.file_open_write_data
   .. automethod:: Brick.file_open_append_data
   .. automethod:: Brick.module_find_first
   .. automethod:: Brick.module_find_next
   .. automethod:: Brick.module_close
   .. automethod:: Brick.poll_command_length
   .. automethod:: Brick.poll_command
   .. automethod:: Brick.boot
   .. automethod:: Brick.bluetooth_factory_reset
