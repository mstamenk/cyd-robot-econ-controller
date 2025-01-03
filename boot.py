'''
Custom Driver xpt2046_cyd and MPY-LVGL build from
https://stefan.box2code.de/2023/11/18/esp32-grafik-mit-lvgl-und-micropython/

Running on cheap yellow display with TWO USB Ports
--> https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/cyd.md
'''

import lvgl as lv
import time
import display_driver
from testing_app import create_testing_page
from sorting_inputs import sorting_inputs  # Import the sorting logic

backlight = display_driver.backlight

# Add this function to handle screen control
def toggle_screen(e,next_btn, sort_btn):
    backlight.value(0)  # Turn off screen
    next_btn.add_flag(lv.obj.FLAG.HIDDEN)
    sort_btn.add_flag(lv.obj.FLAG.HIDDEN)

# Add this to handle any touch event
def on_touch(e,next_btn,sort_btn):
    backlight.value(1)  # Turn screen back on
    next_btn.clear_flag(lv.obj.FLAG.HIDDEN)
    sort_btn.clear_flag(lv.obj.FLAG.HIDDEN)

# Callback to navigate to a new page
def open_page(page_name):
    if page_name == "Testing Page":
        testing_page = create_testing_page(scr)
        lv.scr_load(testing_page)
        return

    if page_name == "Sorting Page":
        sorting_inputs(scr)  # Call the sorting input page
        return

    # Create a new screen for other pages
    new_page = lv.obj()
    new_page.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

    # Add a label to indicate the page name
    titleLbl = lv.label(new_page)
    titleLbl.set_text(page_name)
    titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
    titleLbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    titleLbl.align(lv.ALIGN.TOP_MID, 0, 10)

    # Add a back button to return to the main page
    backBtn = lv.btn(new_page)
    backBtn.set_size(100, 50)
    backBtn.align(lv.ALIGN.BOTTOM_MID, 0, -10)
    backBtn.add_event_cb(lambda e: lv.scr_load(scr), lv.EVENT.CLICKED, None)

    backBtnLbl = lv.label(backBtn)
    backBtnLbl.set_text("Back")
    backBtnLbl.center()

    # Load the new page
    lv.scr_load(new_page)

# Callback functions for buttons
def on_testing_click(e):
    open_page("Testing Page")

def on_sorting_click(e):
    open_page("Sorting Page")

# Get reference to active screen

scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

# Create and position title
titleLbl = lv.label(scr)
titleLbl.set_text("ECON robot controller")
titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
titleLbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
titleLbl.align(lv.ALIGN.TOP_MID, 0, 10)  # Positioned near the top center

# Create Testing button
testingBtn = lv.btn(scr)
testingBtn.set_size(100, 50)
testingBtn.align(lv.ALIGN.LEFT_MID, 20, 0)  # Positioned on the left
testingBtn.add_event_cb(lambda e: on_testing_click(e), lv.EVENT.CLICKED, None)

testingBtnLbl = lv.label(testingBtn)
testingBtnLbl.set_text("Testing")
testingBtnLbl.center()

# Create Sorting button
sortingBtn = lv.btn(scr)
sortingBtn.set_size(100, 50)
sortingBtn.align(lv.ALIGN.RIGHT_MID, -20, 0)  # Positioned on the right
sortingBtn.add_event_cb(on_sorting_click, lv.EVENT.CLICKED, None)

sortingBtnLbl = lv.label(sortingBtn)
sortingBtnLbl.set_text("Sorting")
sortingBtnLbl.center()

# After your other buttons, add a power button
powerBtn = lv.btn(scr)
powerBtn.set_size(50, 50)  # Smaller button
powerBtn.align(lv.ALIGN.BOTTOM_MID, 0, -10)  # Position at bottom
powerBtn.add_event_cb(lambda e: toggle_screen(e,testingBtn, sortingBtn), lv.EVENT.CLICKED, None)
powerBtnLbl = lv.label(powerBtn)
powerBtnLbl.set_text("Off")
powerBtnLbl.center()

# Add touch handler to the main screen
scr.add_event_cb(lambda e: on_touch(e,testingBtn,sortingBtn), lv.EVENT.PRESSED, None)

# Main loop
while True:
    time.sleep(1)
