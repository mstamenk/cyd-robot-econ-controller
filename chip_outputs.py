import lvgl as lv
from init_sorting import create_init_sorting_page

# Function to handle button presses
def button_event_handler(e):
    btn = e.get_target()
    label = btn.get_child(0)  # Assuming the label is the first child
    print(f"Button clicked: {label.get_text()}")

    if btn.get_state() & lv.STATE.CHECKED:
        btn.clear_state(lv.STATE.CHECKED)
    else:
        btn.add_state(lv.STATE.CHECKED)


def create_chip_input(parent, x_offset, y_offset,next_btn):
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
    
    def on_textarea_clicked(evt,next_btn):
        keyboard.clear_flag(lv.obj.FLAG.HIDDEN)
        code = evt.get_code()
        if code == lv.EVENT.CLICKED:
            keyboard.clear_flag(lv.obj.FLAG.HIDDEN)
            next_btn.add_flag(lv.obj.FLAG.HIDDEN)
            
    def on_keyboard_event(evt,next_btn):
        code = evt.get_code()
        if code == lv.EVENT.READY or code == lv.EVENT.CANCEL:
            keyboard.add_flag(lv.obj.FLAG.HIDDEN)
            next_btn.clear_flag(lv.obj.FLAG.HIDDEN)

    chip_input.add_event_cb(lambda e: on_textarea_clicked(e,next_btn), lv.EVENT.CLICKED, None)
    keyboard.add_event_cb(lambda e: on_keyboard_event(e,next_btn), lv.EVENT.ALL, None)
    
    return chip_input, keyboard
    
def on_next_click(e,scr,pressed_inputs,pressed_outputs, chips):
    chip_texts = []
    for i in range(len(chips)):
        chip_texts.append(chips[i].get_text())
    chip_out = '_'.join(chip_texts)
    
    pressed = '_'.join(pressed_outputs)
    inputs = '_'.join(pressed_inputs)

    config = f'{inputs}-{pressed}-{chip_out}'
    create_init_sorting_page(scr,config)



# Page 1: Input trays to sort
def chip_outputs(scr,pressed_inputs,pressed_outputs):
    sorting_inputs = lv.obj()
    sorting_inputs.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    # Back button
    back_btn = lv.btn(sorting_inputs)
    back_btn.set_size(45, 20)
    back_btn.align(lv.ALIGN.TOP_LEFT, 10, 5)
    back_label = lv.label(back_btn)
    back_label.set_text("Back")
    back_label.center()
    back_btn.add_event_cb(lambda e: lv.scr_load(scr), lv.EVENT.CLICKED, None)  # Replace main_menu as necessary

    # Title
    title = lv.label(sorting_inputs)
    title.set_text("Chip number on sorting tray")
    title.align(lv.ALIGN.TOP_MID,  0, 10)

    chips = []

    # Next button
    next_btn = lv.btn(sorting_inputs)
    next_btn.set_size(80, 40)
    next_btn.align(lv.ALIGN.BOTTOM_RIGHT, -10, -10)
    next_label = lv.label(next_btn)
    next_label.set_text("Next")
    next_label.center()

    for i in range(len(pressed_outputs)):
        chip_output, keyboard = create_chip_input(sorting_inputs,10 + i * 105, 100,next_btn)
        chips.append(chip_output)

    next_btn.add_event_cb(lambda e: on_next_click(e,sorting_inputs,pressed_inputs,pressed_outputs,chips), lv.EVENT.CLICKED, None)
    lv.scr_load(sorting_inputs)
