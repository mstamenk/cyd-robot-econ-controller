import lvgl as lv
import machine
import time
import display_driver

backlight = display_driver.backlight

# Add this function to handle screen control
def toggle_screen(e):
    backlight.value(0)  # Turn off screen


# Add this to handle any touch event
def on_touch(e):
    backlight.value(1)  # Turn screen back on


uart = machine.UART(1, 
    baudrate=9600,
    tx=1, 
    rx=3,
    bits=8,
    parity=None,
    stop=1,
    timeout=1000,
    timeout_char=10
)

def read_uart_timeout(uart, timeout):
    """
    Read from UART with timeout
    
    Args:
        uart: UART object
        timeout_ms: timeout in milliseconds
        
    Returns:
        bytes: received data or None if timeout occurred
    """
    start = time.time()
    
    # Wait for data to become available or timeout
    while not uart.any():
        if time.time()- start > timeout:
            return None
        time.sleep(0.1)  # Small delay to prevent busy waiting
    
    # Once data is available, read it
    try:
        return uart.read()
    except Exception as e:
        print(f"Error reading UART: {e}")
        return None


# Callback for Back button (go back to previous page)
def on_back_click(e, testing_page):
    print("Going back to the testing configuration page...")
    lv.scr_load(testing_page)  # Load the testing page

def on_initialize_click(e, connection_text,uart):
    print("Initializing...")
    connection_text.set_text("Status: Initializing...")

    text = ''

    try:
        # 1. Ping the server
        uart.write("PING\n")  # Send the ping message to the server
        #time.sleep(5)  # Wait for a response
        #uart.write(uart.read()+'\n')
        
        #if uart.any():
        #response = uart.read()  # Read the response from the server
        response = read_uart_timeout(uart, 6)
        if response == b'PONG\n':
            text += "Status: Server responded (PONG)\n"
            connection_text.set_text(text)
        else:
            text += f"Status: Unexpected response\n{response}"
            connection_text.set_text(text)
            return
        #else:
        #    text += "Status: No response from server\n"
        #    connection_text.set_text("Status: No response from server")
        #    return

        # 2. Initialize Socket A
        uart.write("INIT_SOCKET_A\n")
        #time.sleep(10)

        #if uart.any():
        #response = uart.read()
        response = read_uart_timeout(uart,10)
        if response == b'OK_A\n':
            text += "Socket A initialized successfully\n"
            print("Socket A initialized successfully")
            connection_text.set_text(text)

        else:
            text += f"Status: Error initializing Socket A\n {response}"
            connection_text.set_text(text)
            return
        #else:
        #    text += "Status: No response for Socket A\n"
        #    connection_text.set_text(text)
        #    return

        # 3. Initialize Socket B
        uart.write("INIT_SOCKET_B\n")
        #time.sleep(10)

        #if uart.any():
        #response = uart.read()
        response = read_uart_timeout(uart,10)
        if response == b'OK_B\n':
            text += "Socket B initialized successfully\n"
            print("Socket B initialized successfully")
            connection_text.set_text(text)

        else:
            text += f"Status: Error initializing Socket B\n{response}"
            connection_text.set_text(text)
            return
        #else:
        #    text += "Status: No response for Socket B\n"
        #    connection_text.set_text(text)
        #    return

        # 4. Check GPIB Status
        uart.write("CHECK_GPIB\n")
        #time.sleep(10)

        #if uart.any():
        #response = uart.read()
        response = read_uart_timeout(uart,6)
        if response == b'GPIB_OK\n':
            text += "GPIB running successfully\n"
            print("GPIB running successfully")
            connection_text.set_text(text)

        else:
            text += f"Status: Error with GPIB\n{response}"
            connection_text.set_text(text)
            return
        #else:
        #    text += "Status: No response for GPIB\n"
        #    connection_text.set_text(text)
        #    return

        # If everything is successful
        text += "Status: Ready to start\n"
        connection_text.set_text(text)

    except Exception as e:
        print(f"Error during communication: {e}")
        connection_text.set_text(f"Status: Error - {e}")
# Callback for Start button
def on_start_click(e, connection_text,init_btn, start_btn, power_btn,config_a, config_b, uart, yes_btn, no_btn):
    print("Starting...")
    current_status = connection_text.get_text()

    # Check if the state is "Ready to start"
    if "Ready to start" in current_status:
        try:
            # Send configuration data to the server
            message = f"START,{config_a},{config_b}\n"  # Format the message
            uart.write(message)  # Send the message to the server
            print(f"Sent to server: {message}")

            #time.sleep(2)  # Wait for acknowledgment from the server

            # Check for a response
            #if uart.any():
            #response = uart.read().strip()  # Read and strip the response
            response = read_uart_timeout(uart,10)
            response = response.strip()
            if response == b'START_OK':
                connection_text.set_text("Status: Robot started successfully")
                print("Robot started successfully")
                init_btn.add_flag(lv.obj.FLAG.HIDDEN)
                start_btn.add_flag(lv.obj.FLAG.HIDDEN)
                power_btn.clear_flag(lv.obj.FLAG.HIDDEN)

            elif response == b'RUNNING_ALREADY':
                connection_text.set_text("Kill run_robot_2hexa.py script?")
                print("Robot is already running. Asking user for action.")

                # Show Yes/No buttons for the user to decide
                yes_btn.clear_flag(lv.obj.FLAG.HIDDEN)
                no_btn.clear_flag(lv.obj.FLAG.HIDDEN)
                
            else:
                connection_text.set_text(f"Status: Unexpected response from server\n{response}")
                print(f"Unexpected response: {response}")
            #else:
            #    connection_text.set_text("Status: No response from server")
            #    print("No response from server")
        except Exception as e:
            print(f"Error during start: {e}")
            connection_text.set_text(f"Status: Error - {e}")
    else:
        print("Cannot start: Initialization incomplete")
        connection_text.set_text("Status: Initialization incomplete")


def on_kill_confirm(e, connection_text, uart, kill, yes_btn, no_btn):
    try:
        if kill:
            print("Sending kill command to local PC...")
            uart.write("KILL\n")  # Send the kill command to the local PC
            #time.sleep(2)

            #if uart.any():
            #response = uart.read().strip()
            response = read_uart_timeout(uart,10)
            response = response.strip()
            if response == b'KILL_OK':
                connection_text.set_text(
                    "Status: Previous script terminated. \nReady to start.\nPress START again"
                )
                print("Previous script terminated. Ready to start.")
            else:
                connection_text.set_text(
                    f"Status: Failed to terminate script. \nPlease try again.\n{response}"
                )
                print("Failed to terminate script.")
        else:
            connection_text.set_text(
                "Status: No response to kill command.\n Please check the connection."
            )
            print("No response to kill command.")
        #else:
        #    connection_text.set_text("Status: Nothing to be done \nRobot already running.")
        #    print("User chose not to kill the running script.")
    except Exception as e:
        print(f"Error sending kill command: {e}")
        connection_text.set_text(f"Status: Error - {e}")

    # Hide Yes/No buttons after the decision
    yes_btn.add_flag(lv.obj.FLAG.HIDDEN)
    no_btn.add_flag(lv.obj.FLAG.HIDDEN)


# Create the Initialization Robot page
def create_init_robot_page(testing_page,config_a, config_b):
    # Create a new screen for the Robot Initialization
    init_page = lv.obj()
    init_page.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    # Title
    titleLbl = lv.label(init_page)
    titleLbl.set_text("Robot Initialization")
    titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
    titleLbl.align(lv.ALIGN.TOP_MID, 0, 10)

    # Create Back Button (go back to the testing page)
    back_btn = lv.btn(init_page)
    back_btn.set_size(45, 20)
    back_btn.align(lv.ALIGN.TOP_LEFT, 10, 5)  # Align at the top-left corner
    back_btn.add_event_cb(lambda e: on_back_click(e, testing_page), lv.EVENT.CLICKED, None)

    back_lbl = lv.label(back_btn)
    back_lbl.set_text("Back")
    back_lbl.center()

    # Create Initialize Button
    init_btn = lv.btn(init_page)
    init_btn.set_size(80, 40)
    init_btn.align(lv.ALIGN.BOTTOM_LEFT, 0, -20)
    init_btn.add_event_cb(lambda e: on_initialize_click(e, connection_text,uart), lv.EVENT.CLICKED, None)

    init_lbl = lv.label(init_btn)
    init_lbl.set_text("Initialize")
    init_lbl.center()

    # Create Yes Button
    yes_btn = lv.btn(init_page)
    yes_btn.set_size(60, 40)
    yes_btn.align(lv.ALIGN.TOP_RIGHT, -70, 50)
    yes_btn.add_flag(lv.obj.FLAG.HIDDEN)  # Initially hidden

    yes_lbl = lv.label(yes_btn)
    yes_lbl.set_text("Yes")
    yes_lbl.center()

    # Create No Button
    no_btn = lv.btn(init_page)
    no_btn.set_size(60, 40)
    no_btn.align(lv.ALIGN.TOP_RIGHT, 0, 50)
    no_btn.add_flag(lv.obj.FLAG.HIDDEN)  # Initially hidden

    no_lbl = lv.label(no_btn)
    no_lbl.set_text("No")
    no_lbl.center()

    # Attach Yes/No buttons to the callback
    yes_btn.add_event_cb(lambda e: on_kill_confirm(e, connection_text, uart, True, yes_btn, no_btn), lv.EVENT.CLICKED, None)
    no_btn.add_event_cb(lambda e: on_kill_confirm(e, connection_text, uart, False, yes_btn, no_btn), lv.EVENT.CLICKED, None)


    # After your other buttons, add a power button
    powerBtn = lv.btn(init_page)
    powerBtn.set_size(50, 50)  # Smaller button
    powerBtn.align(lv.ALIGN.BOTTOM_MID, 0, -10)  # Position at bottom
    powerBtn.add_event_cb(lambda e: toggle_screen(e,), lv.EVENT.CLICKED, None)
    powerBtnLbl = lv.label(powerBtn)
    powerBtnLbl.set_text("Off")
    powerBtnLbl.center()
    powerBtn.add_flag(lv.obj.FLAG.HIDDEN)

    init_page.add_event_cb(lambda e: on_touch(e,), lv.EVENT.PRESSED, None)

    # Create Start Button
    start_btn = lv.btn(init_page)
    start_btn.set_size(80, 40)
    start_btn.align(lv.ALIGN.BOTTOM_RIGHT, 0, -20)
    start_btn.add_event_cb(lambda e: on_start_click(e, connection_text,init_btn,start_btn,powerBtn,config_a, config_b,uart,yes_btn,no_btn), lv.EVENT.CLICKED, None)

    start_lbl = lv.label(start_btn)
    start_lbl.set_text("Start")
    start_lbl.center()

    # Create a connection status text box
    connection_text = lv.label(init_page)
    connection_text.set_text("Status: Not initialized \n Takes 15 seconds to initialize \n Takes 15 seconds to start")
    connection_text.align(lv.ALIGN.LEFT_MID, 10, 0)





     

    return init_page