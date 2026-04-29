## 3/23 Working on Setting up Lidar Device

Our PI device was not recognizing the lidar as a actual USB device. What ended up solving this issue was connecting it to a different port on our Raspberry Pi. It then showed up in /dev/USBtty0

## 3/25 Configuring Lidar.py to work with the lidar

The device was not giving an output while using the correct lidar python library. The issue seemed to be how we were parsing the data the lidar was sending to our program. AI was able to create a test.py program that ran through and reset the lidar and then ran tests to see if it was working correctly. With some tinkering we were able to make that work. 

## 3/30 Device was locking the wheels the wrong way

When you stepped in front of the robot you could not go backwards and when you were behind you could not go forwards. We initially tried to fix it in the code, however since these functions were so deeply embedded in the code we ended up just turning the physical device around.

## 3/30 Website showing reversed to what was happening.

Since we switched the facing angle of the lidar device we needed to update the programs website with the correct facing direction. This was a simple fix.

