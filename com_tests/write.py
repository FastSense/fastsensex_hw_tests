import os
import serial

print("Write")
data = os.urandom(1024*1024)
byte_data = bytearray(data)

incremented_packs = 0
corrupted_packs = 0
start_timeouts = 0

with serial.Serial('/dev/ttyUSB0', 200000, timeout=3) as ser:
    for pack_num in range(0, len(byte_data), 8):
        pack = byte_data[pack_num: pack_num + 8]
        ser.write(pack)

        read_data = ser.read(8)
        for byte in range(len(pack)):
            if pack[byte] >= 255:
                pack[byte] = 0
            else:
                pack[byte] = pack[byte] + 1

        if read_data == pack:
            incremented_packs += 1
        else:
            corrupted_packs += 1

        print("\r{} / {}".format(incremented_packs, corrupted_packs)),
