import lvgl as lv
from init_robot import create_init_robot_page

def on_button_click(e):
    btn = e.get_target()
    label = btn.get_child(0)  # Assuming the label is the first child
    print(f"Button clicked: {label.get_text()}")
    
    # Toggle the state of the button
    if btn.get_state() & lv.STATE.CHECKED:
        btn.clear_state(lv.STATE.CHECKED)
    else:
        btn.add_state(lv.STATE.CHECKED)

    # Update the configuration text
    update_config()

# Create radio buttons for a socket
def create_radio_buttons(parent, options, x_offset, y_offset, title):
    radio_label = lv.label(parent)
    radio_label.set_text(title)
    radio_label.align(lv.ALIGN.TOP_LEFT, x_offset, y_offset)
    
    buttons = []

    for i, option in enumerate(options):
        btn = lv.btn(parent)
        btn.set_size(60, 30)  # Smaller buttons
        btn.align(lv.ALIGN.TOP_LEFT, x_offset + i * 70, y_offset + 20)
        btn.add_event_cb(on_button_click, lv.EVENT.CLICKED, None)

        lbl = lv.label(btn)
        lbl.set_text(option)
        lbl.center()
        
        buttons.append(btn)
        
    return buttons

# Create multi-select buttons (numbers in a horizontal layout)
def create_multi_select_buttons(parent, labels, x_offset, y_offset):
    buttons = []
    for i, label in enumerate(labels):
        btn = lv.btn(parent)
        btn.set_size(30, 30)  # Smaller buttons
        btn.align(lv.ALIGN.TOP_LEFT, x_offset + i * 35, y_offset)
        btn.add_event_cb(on_button_click, lv.EVENT.CLICKED, None)

        lbl = lv.label(btn)
        lbl.set_text(label)
        lbl.center()
        buttons.append(btn)
    return buttons

def create_chip_input(parent, x_offset, y_offset):
    chip_label = lv.label(parent)
    chip_label.set_text("Chip:")
    chip_label.align(lv.ALIGN.TOP_LEFT, x_offset, y_offset)
    
    chip_input = lv.textarea(parent)
    chip_input.set_one_line(True)
    chip_input.set_width(60)
    chip_input.set_text("1")
    chip_input.align(lv.ALIGN.TOP_LEFT, x_offset + 40, y_offset)
    
    keyboard = lv.keyboard(parent)
    keyboard.set_size(320, 80)  # Single row height
    keyboard.set_mode(lv.keyboard.MODE.NUMBER)
    keyboard.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    keyboard.set_textarea(chip_input)
    keyboard.add_flag(lv.obj.FLAG.HIDDEN)  # Hide keyboard

    
    def on_textarea_clicked(evt):
        config_text_a.add_flag(lv.obj.FLAG.HIDDEN)
        config_text_b.add_flag(lv.obj.FLAG.HIDDEN)
        keyboard.clear_flag(lv.obj.FLAG.HIDDEN)
        code = evt.get_code()
        if code == lv.EVENT.CLICKED:
            keyboard.clear_flag(lv.obj.FLAG.HIDDEN)
            
    def on_keyboard_event(evt):
        code = evt.get_code()
        if code == lv.EVENT.READY or code == lv.EVENT.CANCEL:
            keyboard.add_flag(lv.obj.FLAG.HIDDEN)
            update_config()
            config_text_a.clear_flag(lv.obj.FLAG.HIDDEN)
            config_text_b.clear_flag(lv.obj.FLAG.HIDDEN)
            
    
    chip_input.add_event_cb(on_textarea_clicked, lv.EVENT.CLICKED, None)
    keyboard.add_event_cb(on_keyboard_event, lv.EVENT.ALL, None)
    
    return chip_input, keyboard
    
   

# Callback for Back button (go back to previous page)
def on_back_click(e,main_page):
    print("Going back to the previous page...")
    # Here you can add logic to load the previous screen or page.
    lv.scr_load(main_page)  # Assuming you keep track of the previous page

# Callback for Next button (go to next page)
def on_next_click(e,testing_page):
    print("Going to the next page...")

    text_a = config_text_a.get_text()
    text_b = config_text_b.get_text()

    if 'ISSUE' in text_a: 
        print(f'Issue: {text_a}')
    elif 'ISSUE' in text_b: 
        print(f'Issue: {text_b}')
    else:
        lv.scr_load(create_init_robot_page(testing_page,text_a,text_b))  # Load the next page (to be implemented later)

# Update the configuration text
def update_config():
    # Check states for each set of buttons
    a_ec, b_ec = "", ""
    a_trays, b_trays = "", ""
    chip_a, chip_b = "", ""
    
    # Check ECON buttons for both A and B
    if type_a[0].get_state() & lv.STATE.CHECKED and type_a[1].get_state() & lv.STATE.CHECKED:
        a_ec = "ISSUE"
    elif type_a[0].get_state() & lv.STATE.CHECKED:
        a_ec = 'ECOND'
    elif type_a[1].get_state() & lv.STATE.CHECKED:
        a_ec = "ECONT"
      
    if type_b[0].get_state() & lv.STATE.CHECKED and type_b[1].get_state() & lv.STATE.CHECKED:
        b_ec = 'ISSUE'
    elif type_b[0].get_state() & lv.STATE.CHECKED:
        b_ec = "ECOND"
    elif type_b[1].get_state() & lv.STATE.CHECKED:
        b_ec = "ECONT"
    
    # Check tray buttons for both A and B
    a_trays = [btn.get_child(0).get_text() for btn in trays_a if btn.get_state() & lv.STATE.CHECKED]
    b_trays = [btn.get_child(0).get_text() for btn in trays_b if btn.get_state() & lv.STATE.CHECKED]

    a_trays_label = ' '.join(a_trays)
    b_trays_label = ' '.join(b_trays)

    if a_trays_label == '': a_trays_label = 'ISSUE'
    if b_trays_label == '': b_trays_label = 'ISSUE'

    # Check chip inputs for A and B
    chip_a = chip_a_input.get_text()
    chip_b = chip_b_input.get_text()

    if int(chip_a) < 1: chip_a = str(1) # Make sure one can't input too high or low numbers
    if int(chip_a) > 90: chip_a = str(90)
    
    if int(chip_b) < 1: chip_b = str(1)
    if int(chip_b) > 90: chip_b = str(90)

    # Handle both ECON buttons being checked (issue case)

    config_text_a.set_text(f"A: {a_ec} - {a_trays_label} - {chip_a}")
    config_text_b.set_text(f"B: {b_ec} - {b_trays_label} - {chip_b}")





# Create the testing configuration page
def create_testing_page(main_page):
    # Create a new screen for the Testing Configuration
    testing_page = lv.obj()
    testing_page.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    # Title
    titleLbl = lv.label(testing_page)
    titleLbl.set_text("Testing Configuration")
    titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
    titleLbl.align(lv.ALIGN.TOP_MID, 0, 10)
    
    # Create radio buttons for Socket A and Socket B
    global type_a, type_b
    type_a = create_radio_buttons(testing_page, ["ECOND", "ECONT"], 10, 30, "Socket A")
    type_b = create_radio_buttons(testing_page, ["ECOND", "ECONT"], 170, 30, "Socket B")

    # Create number buttons in a horizontal layout, smaller size
    global trays_a,trays_b
    trays_a = create_multi_select_buttons(testing_page, ["1", "2", "3", "4"], 10, 85)
    trays_b = create_multi_select_buttons(testing_page, ["5", "6", "7", "8"], 170, 85)

    # Create chip number input
    global chip_a_input, chip_b_input
    chip_a_input, key_a = create_chip_input(testing_page, 10, 120)
    chip_b_input, key_b = create_chip_input(testing_page, 170, 120)

    # Create Back Button
    back_btn = lv.btn(testing_page)
    back_btn.set_size(45, 20)
    back_btn.align(lv.ALIGN.TOP_LEFT, 10, 5)  # Align at the bottom-left
    back_btn.add_event_cb(lambda e: on_back_click(e,main_page), lv.EVENT.CLICKED, None)

    back_lbl = lv.label(back_btn)
    back_lbl.set_text("Back")
    back_lbl.center()

    # Create Next Button
    next_btn = lv.btn(testing_page)
    next_btn.set_size(45, 20)
    next_btn.align(lv.ALIGN.TOP_RIGHT, -20, 5)  # Align at the bottom-right
    next_btn.add_event_cb(lambda e: on_next_click(e,testing_page), lv.EVENT.CLICKED, None)

    next_lbl = lv.label(next_btn)
    next_lbl.set_text("Next")
    next_lbl.center()
    
        # Configuration Text (lower part of the screen)
    global config_text_a, config_text_b
    config_text_a = lv.label(testing_page)
    config_text_a.set_text("A: ISSUE")
    config_text_a.align(lv.ALIGN.BOTTOM_LEFT, 10, -30)
    
    config_text_b = lv.label(testing_page)
    config_text_b.set_text("B: ISSUE")
    config_text_b.align(lv.ALIGN.BOTTOM_LEFT, 10, -10)

    return testing_page