import os
import sys
import serial

ma4_port_map = ['/dev/ttyS5', '/dev/ttyS4']
ma5_port_map = ['/dev/ttyS6', '/dev/ttyS5']
device_list = [('Conga-ma4', ma4_port_map), ('Conga-ma5', ma5_port_map)]

# Parameters of the uart/usb loopback test
# Number of passed packs
usb_uart_packs = 128
# Pack size in byte
usb_uart_pack_size = 1024
# Port baudrate
usb_uart_speed = 921600


# Parameters of the simple loopback test
simple_packs = 1024
simple_pack_size = 1
simple_speed = 9600


def device_select(device_list):
    device = ""

    print('Chose device from list:')
    for device_id in range(len(device_list)):
        print("    {}: {}".format(device_list[device_id][0], device_id + 1))
    print("    Exit: q")

    while not device:
        try:
            key = input('Device: ')

            if key == "q" or key == "Q":
                print("Exiting...")
                sys.exit()

            device = int(key) - 1
            if device < len(device_list):
                device_name = device_list[device][0]
                port_map = device_list[device][1]
                return device_name, port_map
            else:
                raise ValueError
        except ValueError:
            print("Bad device id. Please select one from device list")


def loopback_type_select():
    loopback_type = 0
    print('Chose lopback test type:')
    print('    Simple: 1. To check if the port is working')
    print('    USB/UART: 2. To test port speed')


    while not loopback_type:
        try:
            key = input('Device: ')

            if key == "q" or key == "Q":
                print("Exiting...")
                sys.exit()

            loopback_type = int(key)
            if loopback_type == 1 or loopback_type == 2:
                return loopback_type
            else:
                raise ValueError
        except ValueError:
            loopback_type = 0
            print("Bad loopback id. Please select one from list")


def com_port_select(devise_name, port_map):
    com_port = ""

    print("Selected COM module version: {}. Select the com port to be tested:".format(devise_name))
    for port_id in range(len(port_map)):
        print("    COM{}({}): {}".format(port_id, port_map[port_id], port_id + 1))
    print("    Exit: q")

    while not com_port:
        try:
            key = input('Port: ')

            if key == "q" or key == "Q":
                print("Exiting...")
                sys.exit()

            com_port_id = int(key) - 1
            if com_port_id < len(port_map):
                com_port = port_map[com_port_id]
                return com_port
            else:
                raise ValueError
        except ValueError:
            print("Bad COM port id. Please select one from port list")
            continue


def simple_loopback(com_port_name, com_speed, packet_number=1024, packet_size=1):
    checked_packs = 0
    corrupted_packs = 0
    timeout_counter = 0

    try:
        with serial.Serial(com_port_name, com_speed, timeout=1) as com_port:
            print("\nPacks statistic:")
            for pack_id in range(packet_number):
                pack = os.urandom(packet_size)
                com_port.write(pack)

                read_data = com_port.read(packet_size)

                if len(read_data) != packet_size:
                    timeout_counter += 1
                if timeout_counter >= 10:
                    break

                if read_data == pack:
                    checked_packs += 1
                else:
                    corrupted_packs += 1
                com_port.reset_input_buffer()

                print("\rPassed: {}, checked: {}, corrupted {}".format(pack_id, checked_packs, corrupted_packs), end='')

            print()
            if checked_packs == pack_id + 1:
                print("Speed loopback test. Port: {}. Pass".format(com_port_name))
                print("\33[32mPass\33[0m")
            else:
                print("Speed loopback test. Port: {}. Failed".format(com_port_name))
                if timeout_counter >= 10:
                    print("Timeout exit")
                print("\33[31mFailed\33[0m")

    except serial.serialutil.SerialException as serial_fail:
        print(serial_fail)
        print("Exiting...")
        sys.exit()


def speed_loopback(com_port_name, usb_port_name, speed, packet_number=1024, packet_size=1024):
    checked_packs = 0
    corrupted_packs = 0
    timeout_counter = 0

    try:
        with serial.Serial(com_port_name, speed, timeout=1) as com_port, \
             serial.Serial(usb_port_name, speed, timeout=1) as usb_port:
            print("Packs statistic:")
            for pack_id in range(packet_number):
                pack = bytearray(os.urandom(packet_size))
                com_port.write(pack)

                usb_read_pack = bytearray(usb_port.read(packet_size))

                if len(usb_read_pack) != packet_size:
                    timeout_counter += 1
                if timeout_counter >= 10:
                    break

                for byte in range(len(pack)):
                    if pack[byte] >= 255:
                        pack[byte] = 0
                    else:
                        pack[byte] = pack[byte] + 1

                for byte in range(len(usb_read_pack)):
                    if usb_read_pack[byte] >= 255:
                        usb_read_pack[byte] = 0
                    else:
                        usb_read_pack[byte] = usb_read_pack[byte] + 1

                usb_port.write(usb_read_pack)

                com_read_pack = com_port.read(packet_size)

                if com_read_pack == pack:
                    checked_packs += 1
                else:
                    corrupted_packs += 1
                com_port.reset_input_buffer()
                usb_port.reset_input_buffer()

                print("\rPassed: {}, checked: {}, corrupted {}".format(pack_id + 1, checked_packs, corrupted_packs), end='')

            print()
            if checked_packs == pack_id + 1:
                print("Speed loopback test. Port: {}.".format(com_port_name))
                print("\33[32mPass\33[0m")
            else:
                print("Speed loopback test. Port: {}. Failed".format(com_port_name))
                if timeout_counter >= 10:
                    print("Timeout exit")
                print("\33[31mFailed\33[0m")


    except serial.serialutil.SerialException as serial_fail:
        print(serial_fail)
        print("Exiting...")
        sys.exit()


if __name__ == "__main__":
    finish = False

    device, port_map = device_select(device_list)

    loopback_type = loopback_type_select()

    while not finish:
        com_port = com_port_select(device, port_map)

        print("Selected device: {}, tested port {}".format(device, com_port))

        if loopback_type == 1:
            simple_loopback(com_port, simple_speed, packet_number=simple_packs, packet_size=simple_pack_size)
        elif loopback_type == 2:
            speed_loopback(com_port, '/dev/ttyUSB0', usb_uart_speed, packet_number=usb_uart_packs, packet_size=usb_uart_pack_size)

        print("Enter 'q' to exit or another button to select port\n")
        key = input()
        if key == "q":
            finish = True
