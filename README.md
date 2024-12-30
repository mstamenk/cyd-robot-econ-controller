# cyd-messaging-app
Cheap Yellow Display - Robot controller


# Installation on macos

The framework consists of a ESP32 firmware using the `lvgl` library for button displays, `x2046pt` and `ili9341` to control the touch screen and print text and messages. 

Instructions are based of [ESP32-Cheap-Yellow-Display-Micropython-LVGL|https://github.com/de-dh/ESP32-Cheap-Yellow-Display-Micropython-LVGL]. The IDE used is `Thonny`. 

First, one needs to download the firmware:

```
git clone git@github.com:mstamenk/cyd-robot-econ-controller.git
cd cyd-robot-econ-controller.git

curl https://stefan.box2code.de/wp-content/uploads/2024/04/lv_micropython-WROOM_AOIEspNow.zip -o lv_micropython-WROOM_AOIEspNow.zip 
unzip lv_micropython-WROOM_AOIEspNow.zip
```

Then one needs to install the firmware on the device. For this, we use `esptools` (see `requirements.txt`):
```
pip install -r requirements.txt
```

For the firmware, install it via and edit the `flash.sh` script with the right port:
```
cd lv_micropython-WROOM_AOIEspNow 
source flash.sh # Will erase flash memory and start from scratch
```

## Copying files to the ESP32
In order to copy files, we will use the `ampy` library from adafruit. 

```
ampy --port /dev/tty.usbserial-110 ls # to list files
ampy --port /dev/tty.usbserial-110 put boot.py # copy file or repository to ESP32
ampy --port /dev/tty.usbserial-110 get boot.py # to get the file content
ampy --port /dev/tty.usbserial-110 mkdir repo # to create a repository
ampy --port /dev/tty.usbserial-110 rmdir repo # to remove a repository
```





