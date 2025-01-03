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
def on_back_click(e, testing_page,uart):
    print("Going back to the testing configuration page...")
    uart.deinit()
    uart= None
    lv.scr_load(testing_page)  # Load the testing page

# Callback for Start button
def on_start_click(e, connection_text, start_btn, power_btn,config, uart, yes_btn, no_btn):
    print("Starting...")

    # Check if the state is "Ready to start"
    try:
        # Send configuration data to the server
        message = f"SORT,{config}\n"  # Format the message
        uart.write(message)  # Send the message to the server
        print(f"Sent to server: {message}")

        response = read_uart_timeout(uart,10)
        #response = response.strip()
        if response == b'SORT_OK\n':
            connection_text.set_text("Status: Robot started successfully")
            print("Robot started successfully")
            start_btn.add_flag(lv.obj.FLAG.HIDDEN)
            power_btn.clear_flag(lv.obj.FLAG.HIDDEN)

        elif response == b'SORTING_ALREADY':
            connection_text.set_text("Kill chip_sorting.py script?")
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
    

def on_kill_confirm(e, connection_text, uart, kill, yes_btn, no_btn):
    try:
        if kill:
            print("Sending kill command to local PC...")
            uart.write("KILL_SORT\n")  # Send the kill command to the local PC
            #time.sleep(2)

            #if uart.any():
            #response = uart.read().strip()
            response = read_uart_timeout(uart,10)
            response = response.strip()
            if response == b'KILL_SORT_OK':
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
def create_init_sorting_page(testing_page,config):
    # Create a new screen for the Robot Initialization
    init_page = lv.obj()
    init_page.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    uart = machine.UART(1,  # initialise UART
    baudrate=9600,
    tx=1, 
    rx=3,
    bits=8,
    parity=None,
    stop=1,
    timeout=1000,
    timeout_char=20
    )

    # Title
    titleLbl = lv.label(init_page)
    titleLbl.set_text("Sorting Initialization")
    titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
    titleLbl.align(lv.ALIGN.TOP_MID, 0, 10)

    # Create Back Button (go back to the testing page)
    back_btn = lv.btn(init_page)
    back_btn.set_size(45, 20)
    back_btn.align(lv.ALIGN.TOP_LEFT, 10, 5)  # Align at the top-left corner
    back_btn.add_event_cb(lambda e: on_back_click(e, testing_page, uart), lv.EVENT.CLICKED, None)

    back_lbl = lv.label(back_btn)
    back_lbl.set_text("Back")
    back_lbl.center()

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
    start_btn.align(lv.ALIGN.BOTTOM_LEFT, 5, -20)
    start_btn.add_event_cb(lambda e: on_start_click(e, connection_text,start_btn,powerBtn,config,uart,yes_btn,no_btn), lv.EVENT.CLICKED, None)

    start_lbl = lv.label(start_btn)
    start_lbl.set_text("Start")
    start_lbl.center()

    # Create a connection status text box
    connection_text = lv.label(init_page)
    connection_text.set_text(f"Configuration: {config}")
    connection_text.align(lv.ALIGN.LEFT_MID, 10, 0)

    lv.scr_load(init_page)

    #return init_page