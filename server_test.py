import serial
import time
from serial.serialutil import SerialException

def connect_serial(port='/dev/tty.usbserial-110', baudrate=9600):
    while True:
        try:
            ser = serial.Serial(port=port, baudrate=baudrate, timeout=2)
            print(f"\nConnected to {port} at {baudrate} baud")
            return ser
        except SerialException:
            print(f"\rAttempting to connect to {port}...", end='')
            time.sleep(1)

def run_server():
    ser = None
    
    while True:
        try:
            if ser is None:
                ser = connect_serial()
                
            if ser.in_waiting:
                raw_data = ser.readline()
                try:
                    command = raw_data.decode('ascii', errors='ignore').strip()
                    print(f"Received: {command}")
                    
                    if command == "PING":
                        ser.write(b"PONG\n")
                    elif command == "INIT_SOCKET_A":
                        ser.write(b"OK_A\n")
                    elif command == "INIT_SOCKET_B":
                        ser.write(b"OK_B\n")
                    elif command == "CHECK_GPIB":
                        ser.write(b"GPIB_OK")
                    elif command.startswith("START"):
                        ser.write(b"START_OK")
                        configs = command.split(',')
                        if len(configs) == 3:
                            print(f"Config A: {configs[1]}")
                            print(f"Config B: {configs[2]}")
                except Exception as e:
                    print(f"Error decoding data: {raw_data.hex()}")
            
            time.sleep(0.1)

        except (SerialException, OSError) as e:
            print(f"\nConnection lost: {e}")
            if ser:
                ser.close()
            ser = None
            time.sleep(1)
            
        except KeyboardInterrupt:
            if ser:
                ser.close()
            print("\nServer stopped")
            break

if __name__ == "__main__":
    run_server()