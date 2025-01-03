python3 -m esptool --chip esp32 -p /dev/tty.usbserial-110 -b 460800 --before=default_reset --after=hard_reset erase_flash
python3 -m esptool --chip esp32 -p /dev/tty.usbserial-110 -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB 0x1000 bootloader/bootloader.bin 0x10000 micropython.bin 0x8000 partition_table/partition-table.bin 
