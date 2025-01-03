echo "Boot.py"
ampy --port /dev/tty.usbserial-110 put boot.py
echo "test_app.py"
ampy --port /dev/tty.usbserial-110 put testing_app.py
echo "init_robot.py"
ampy --port /dev/tty.usbserial-110 put init_robot.py
echo "sorting_inputs.py"
ampy --port /dev/tty.usbserial-110 put sorting_inputs.py
echo "sorting_outputs.py"
ampy --port /dev/tty.usbserial-110 put sorting_outputs.py
echo "init_sorting.py"
ampy --port /dev/tty.usbserial-110 put init_sorting.py
echo "chip_outputs.py"
ampy --port /dev/tty.usbserial-110 put chip_outputs.py
echo "fonts"
ampy --port /dev/tty.usbserial-110 put fonts
echo "img"
ampy --port /dev/tty.usbserial-110 put img
echo "lib"
ampy --port /dev/tty.usbserial-110 put lib
echo "log"
ampy --port /dev/tty.usbserial-110 put log
