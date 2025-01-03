import lvgl as lv
from chip_outputs import chip_outputs

# Function to handle button presses
def button_event_handler(e):
    btn = e.get_target()
    label = btn.get_child(0)  # Assuming the label is the first child
    print(f"Button clicked: {label.get_text()}")

    if btn.get_state() & lv.STATE.CHECKED:
        btn.clear_state(lv.STATE.CHECKED)
    else:
        btn.add_state(lv.STATE.CHECKED)

def on_next_click(e,scr,buttons,pressed_inputs):
    pressed_outputs = [btn.get_child(0).get_text() for btn in buttons if btn.get_state() & lv.STATE.CHECKED]
    chip_outputs(scr,pressed_inputs, pressed_outputs)

# Page 1: Input trays to sort
def sorting_outputs(scr,pressed_buttons):
    sorting_outputs = lv.obj()
    sorting_outputs.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    # Back button
    back_btn = lv.btn(sorting_outputs)
    back_btn.set_size(45, 20)
    back_btn.align(lv.ALIGN.TOP_LEFT, 10, 5)
    back_label = lv.label(back_btn)
    back_label.set_text("Back")
    back_label.center()
    back_btn.add_event_cb(lambda e: lv.scr_load(scr), lv.EVENT.CLICKED, None)  # Replace main_menu as necessary

    # Title
    title = lv.label(sorting_outputs)
    title.set_text("Receiving trays for sorting")
    title.align(lv.ALIGN.TOP_MID,  0, 10)

    buttons = []
    # Buttons for trays
    x_offset = 10
    y_offset = 85
    for i in range(8):
        if str(i+1) in pressed_buttons: continue
        btn = lv.btn(sorting_outputs)
        btn.set_size(30, 30)
        btn.align(lv.ALIGN.TOP_LEFT, x_offset + i * 35, y_offset)
        btn_label = lv.label(btn)
        btn_label.set_text(str(i + 1))
        btn_label.center()
        #btn.set_user_data(i + 1)
        btn.add_event_cb(button_event_handler, lv.EVENT.CLICKED, None)
        buttons.append(btn)


    # Next button
    next_btn = lv.btn(sorting_outputs)
    next_btn.set_size(80, 40)
    next_btn.align(lv.ALIGN.BOTTOM_RIGHT, -10, -10)
    next_label = lv.label(next_btn)
    next_label.set_text("Next")
    next_label.center()
    next_btn.add_event_cb(lambda e: on_next_click(e,sorting_outputs,buttons,pressed_buttons), lv.EVENT.CLICKED, None)

    lv.scr_load(sorting_outputs)
