import logging
import serial
import signal
import sys
import time
import paramiko
import os
import argparse
import subprocess

# Global serial connection
ser = None

# Username for SSH connection
USERNAME = "HGCAL_dev"  # Replace with your actual SSH username

# Set up the logger
logging.basicConfig(
    filename='remote_logger.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logging.info("Server script started.")
print("Server script started.")  # Debugging output

# Function to connect to ESP32 via serial
def connect_to_esp32(port):
    global ser
    """Connect to the ESP32 via the specified port."""
    while True:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            logging.info(f"Connected to {port}")
            print(f"Connected to {port}")  # Debugging output
            return ser
        except serial.SerialException:
            logging.warning(f"Could not connect to {port}. Retrying in 3 seconds...")
            print(f"Could not connect to {port}. Retrying in 3 seconds...")  # Debugging output
            time.sleep(3)

# Function to handle script exit and clean up
def handle_exit(signum, frame):
    """Clean up the serial connection on script exit."""
    global ser
    if ser and ser.is_open:
        logging.info("Closing serial connection...")
        print("Closing serial connection...")  # Debugging output
        ser.close()
    logging.info("Exiting the server script.")
    print("Exiting the server script.")  # Debugging output
    sys.exit(0)

# Function to listen for commands from ESP32
def listen_for_commands(local_mode=False):
    """Listen for commands and respond based on the mode (local or remote)."""
    port = '/dev/tty.usbserial-110'  # Update with your correct serial port
    global ser
    ser = connect_to_esp32(port)

    while True:
        try:
            if ser.in_waiting > 0:
                message = ser.readline()
                try:
                    message = message.decode('utf-8').strip()
                except UnicodeDecodeError:
                    logging.error(f"Received non-UTF-8 message: {message}")
                    print(f"Received non-UTF-8 message: {message}")  # Debugging output
                    continue

                logging.info(f"Received command: {message}")
                print(f"Received command: {message}")  # Debugging output

                if message == "PING":
                    logging.info("Sending PONG response.")
                    print("Sending PONG response.")  # Debugging output
                    ser.write("PONG\n".encode('utf-8'))

                elif message.startswith("START"):
                    parts = message.split(',')
                    if len(parts) == 3:
                        config_a = parts[1].strip()
                        config_b = parts[2].strip()
                        logging.info(f"Processing START command with config_a: {config_a}, config_b: {config_b}")
                        print(f"Processing START command with config_a: {config_a}, config_b: {config_b}")  # Debugging output
                        response = handle_start_command(config_a, config_b, local_mode)
                        ser.write(response.encode('utf-8'))

                elif message.startswith("KILL"):
                    logging.info("Processing KILL command.")
                    print("Processing KILL command.")  # Debugging output
                    response = handle_kill_command(local_mode)
                    ser.write(response.encode('utf-8'))

                elif message == "CHECK_GPIB":
                    if local_mode:
                        status = "GPIB_OK" if check_gpib_status() else "GPIB_ERROR"
                        ser.write(f"{status}\n".encode('utf-8'))
                        logging.info(f"CHECK_GPIB result: {status}")
                        print(f"CHECK_GPIB result: {status}")  # Debugging output

                elif message == "INIT_SOCKET_A":
                    result = restart_hexa_job_local('192.168.1.44') if local_mode else restart_hexa_job('192.168.1.44')
                    status = "OK_A" if result else "ERROR_A"
                    ser.write(f"{status}\n".encode('utf-8'))
                    logging.info(f"INIT_SOCKET_A result: {status}")
                    print(f"INIT_SOCKET_A result: {status}")  # Debugging output

                elif message == "INIT_SOCKET_B":
                    result = restart_hexa_job_local('192.168.1.46') if local_mode else restart_hexa_job('192.168.1.46')
                    status = "OK_B" if result else "ERROR_B"
                    ser.write(f"{status}\n".encode('utf-8'))
                    logging.info(f"INIT_SOCKET_B result: {status}")
                    print(f"INIT_SOCKET_B result: {status}")  # Debugging output

                else:
                    logging.warning(f"Unknown command received: {message}")
                    print(f"Unknown command received: {message}")  # Debugging output

        except serial.SerialException:
            logging.error("Connection lost. Attempting to reconnect...")
            print("Connection lost. Attempting to reconnect...")  # Debugging output
            ser.close()
            ser = connect_to_esp32(port)
            
        except OSError as e:
            logging.error(f"Device error: {e}. Attempting to reconnect...")
            print(f"Device error: {e}. Attempting to reconnect...")  # Debugging output
            if ser and ser.is_open:
                ser.close()
            ser = connect_to_esp32(port)

# Function to restart the Hexa job on the remote server (SSH)
def restart_hexa_job(ip):
    """Restart the job on the Hexa controller using passwordless SSH."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key_path = "/path/to/your/private/key"
        ssh.connect(ip, username=USERNAME, key_filename=private_key_path)

        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'hexa_pytest_server.py'")
        output = stdout.read().decode()

        if 'nohup' in output:
            logging.info(f"Job found on {ip}. Killing and restarting...")
            print(f"Job found on {ip}. Killing and restarting...")  # Debugging output
            ssh.exec_command("pkill -f hexa_pytest_server.py")
            time.sleep(1)
            ssh.exec_command("nohup ./hexa_pytest_server.py &")
            logging.info(f"Job restarted on {ip}")
            print(f"Job restarted on {ip}")  # Debugging output
            return True
        else:
            logging.info(f"No job found on {ip}. Starting it...")
            print(f"No job found on {ip}. Starting it...")  # Debugging output
            ssh.exec_command("nohup ./hexa_pytest_server.py &")
            return True

    except Exception as e:
        logging.error(f"Error restarting job on {ip}: {e}")
        print(f"Error restarting job on {ip}: {e}")  # Debugging output
        return False

# Function to restart the Hexa job locally
def restart_hexa_job_local(ip):
    try:
        result = os.popen("ps aux | grep 'hexa_pytest_server.py' | grep -v grep").read()
        if result:
            pid = result.split()[1]
            logging.info(f"Stopping job locally with PID {pid}.")
            print(f"Stopping job locally with PID {pid}.")  # Debugging output
            os.kill(int(pid), signal.SIGTERM)
            time.sleep(1)

        logging.info("Restarting the Hexa job locally.")
        print("Restarting the Hexa job locally.")  # Debugging output
        os.system("nohup ./hexa_pytest_server.py &")
        return True
    except Exception as e:
        logging.error(f"Error restarting Hexa job locally: {e}")
        print(f"Error restarting Hexa job locally: {e}")  # Debugging output
        return False

# Function to check if GPIB server is running
def check_gpib_status():
    try:
        result = os.system("ps aux | grep 'gpib_server.py' | grep -v grep")
        if result == 0:
            logging.info("GPIB server is running.")
            print("GPIB server is running.")  # Debugging output
            return True
        else:
            logging.warning("GPIB server is not running.")
            print("GPIB server is not running.")  # Debugging output
            return False
    except Exception as e:
        logging.error(f"Error checking GPIB status: {e}")
        print(f"Error checking GPIB status: {e}")  # Debugging output
        return False

# Function to handle KILL command
def handle_kill_command(local_mode):
    try:
        find_command = "pgrep -f run_robot_chip_2hexa.py"
        result = subprocess.run(find_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            process_id = result.stdout.strip()
            kill_command = f"kill {process_id}"
            os.system(kill_command)
            logging.info(f"Killed process with PID {process_id}.")
            print(f"Killed process with PID {process_id}.")  # Debugging output
            return "KILL_OK"
        else:
            logging.warning("No matching process found.")
            print("No matching process found.")  # Debugging output
            return "NO_PROCESS"
    except Exception as e:
        logging.error(f"Error handling kill command: {e}")
        print(f"Error handling kill command: {e}")  # Debugging output
        return "ERROR"

# Function to handle START command
def handle_start_command(config_a, config_b, local_mode):
    try:
        find_command = "pgrep -f run_robot_chip_2hexa.py"
        result = subprocess.run(find_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Script is already running.")
            print("Script is already running.")  # Debugging output
            return "RUNNING_ALREADY"

        trays_a = config_a.split(' - ')[1].split(' ')
        trays_b = config_b.split(' - ')[1].split(' ')
        chip_start_a = config_a.split(' - ')[-1]
        chip_start_b = config_b.split(' - ')[-1]

        command = f"nohup ./run_robot_chip_2hexa.py --trays_a {','.join(trays_a)} --trays_b {','.join(trays_b)} --chip_number_start_a {chip_start_a} --chip_number_start_b {chip_start_b} &"
        os.system(command)
        logging.info(f"Started script with command: {command}")
        print(f"Started script with command: {command}")  # Debugging output
        return "START_OK"
    except Exception as e:
        logging.error(f"Error during start command: {e}")
        print(f"Error during start command: {e}")  # Debugging output
        return "ERROR"

# Register the cleanup handler
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for controlling Hexa robot.")
    parser.add_argument('--local', action='store_true', help="Run in local debugging mode.")
    args = parser.parse_args()

    logging.info("Starting command listener.")
    print("Starting command listener.")  # Debugging output
    listen_for_commands(local_mode=args.local)
