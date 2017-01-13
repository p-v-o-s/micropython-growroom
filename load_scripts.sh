#!/bin/bash -x
ampy -p /dev/ttyUSB0 -b 115200 put SECRET_CONFIG.json
ampy -p /dev/ttyUSB0 -b 115200 put network_setup.py
ampy -p /dev/ttyUSB0 -b 115200 put time_manager.py
ampy -p /dev/ttyUSB0 -b 115200 put main.py
