# What is the ScaleLiquidRemainingIOT
The ScaleLiquidRemainingIOT is an Internet of Things device that is used to collect weight data from scales to know the percentage of how full things on them are. This project is initially being designed for the use of beer kegs but can be used in other situations.

# How Does it Work
There are two parts to this project the software part and the hardware part.
  
### Code on the Pi
All of the code that is put on to the Pi is in the [ScaleLiquidRemainingIOT/RaspberryPiCode/](https://github.com/ZackJorquera/ScaleLiquidRemainingIOT/tree/master/RaspberryPiCode) folder. This includes two independent programs: the FLaskApplication and the ScaleDataAggregator. The Flask application uses [Flask](http://flask.pocoo.org/) to display a web-based dashboard. The ScaleDataAggregator collects data from the scales and pushes that data to a database. These two programs launch on the Pi is turned on. Both of these Programs use tools from the [Tools](https://github.com/ZackJorquera/ScaleLiquidRemainingIOT/tree/master/RaspberryPiCode/Tools) subfolder to read or write to the database, read the values on the scales, or to create Bokeh graphs.

### Hardware
This project 


# How to set up
## Things you need
- [Raspberry PI (any model)](https://www.raspberrypi.org/products/)
  - Ability to connect to a local network via ethernet or wireless.
  - [Peripherals for Pi Setup](https://www.raspberrypi.org/documentation/setup/)
  - 5V micro USB power supply
- SD Card

If you want to be able to have the database for historical data you have a couple of options. The easiest solution is to have a second database server to host the database or with Arch Linux ARM you can host the database directly on the pi.


## Set up
The first thing that you need to do is put an operating system on to the SD card. If you are using the Pi model 1, you will need to use an operating system for ARM6. The best are [Raspian](https://www.raspberrypi.org/downloads/raspbian/) or [Arch Linux Arm](https://archlinuxarm.org/platforms/armv6/raspberry-pi), but if you are using a later model, you can also use different distros such as [Ubuntu](https://wiki.ubuntu.com/ARM/RaspberryPi). For the rest of this tutorial, I will be using Raspian. For installing the operating systems, there are good guides in each of the provided links

Download the latest version of [Rasbian](https://www.raspberrypi.org/downloads/raspbian/) (I'm getting version 4.14) and an [IOS Burner](https://etcher.io/). Open the IOS Burner, plug in the micro SD card and burn the image to the sd card. Put the sd card with the burnt image into the pi and turn on the pi.

Raspian is pre-loaded with a lot of bloatware, you can remove it by pasting the following into the Linux terminal.
```
sudo apt-get remove --purge wolfram-engine libreoffice* scratch minecraft-pi sonic-pi dillo gpicview oracle-java8-jdk openjdk-7-jre oracle-java7-jdk openjdk-8-jre geany -y
sudo apt-get autoremove -y
sudo apt-get autoclean -y

```
In order for the scrips to run properly, you will need to install the required libraries.
```
sudo apt-get update -y
sudo apt-get install vim python-dev python-pip python-flask python3-flask -y
sudo pip install --upgrade distribute
sudo pip install ipython
sudo pip install bokeh
sudo pip install pymongo
sudo pip install statistics
sudo pip install --upgrade RPi.GPIO

```
Additionally, the bcm2835 also need to be installed in order for the QuickPulse.c script to work.
```
cd /home/pi/Downloads
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.55.tar.gz
tar -zxvf bcm2835-1.55.tar.gz
cd bcm2835-1.55
./configure
sudo make
sudo make check
sudo make install

```
And then finally, you can download the source code.
```
cd /home/pi/Documents
git clone https://github.com/ZackJorquera/ScaleLiquidRemainingIOT.git

```
And run the setup.sh script
```
bash setup.sh
```

## Run
If everything was set up properly then both the flask app and the aggregator should launch when you call their aliases. Use ```ifconfig``` to get the IP address of the pi (eth0 for ethernet and wlan0 for wireless), this is what you use for the URL to the flask web site. The flask app should be at ```http://<ip address of the pi>:5000/```
If you want to have everything run on startup you must add the following line to the file /etc/rc.local before the exit call on the PI.
```
startflaskapp
startscaleagreggator
```
Additionally, you can set up ssh to be able to connect to the pi from an external computer. Because the default version in raspbian does not work you will have to reinstall it.
```
sudo apt-get install --reinstall openssh-server
```
To connect to the pi with ssh use [PuTTY](https://www.putty.org/) if you are on windows, or run the following command for Linux or macOS
```
ssh pi@<ip address of the pi>
```
Use 'raspberry' as the password. You might need to [create an ssh key](https://confluence.atlassian.com/bitbucketserver/creating-ssh-keys-776639788.html) if you haven't already.

## Use
Now that everything has been set up, you are now able to plug in the scales and start reading scale data. Each HX711 chip has 5 outputs that you will need to plug in. Use the below image to know what each GPIO pin does. Remember to turn the Pi off before plugging in any pins.
First, you need to plug in the 3.3v (the VDD pin) and the 5v(the VCC pin) power as well as the ground into their respective GPIO pins. If you are using more than to HX711 chips you will need to connect the power pins in parallel. Now, with the two remaining pins, the data and clock pins, you will need to plug them into two of GPIO labeled pins, It really doesn't matter which pins you use, but try to avoid pins with alternate purposes (use the green pin in the image). Record down their GPIO numbers (not the pin numbers).
In the flask app, when creating a new scale, input those GPIO nums that you plugged the data and clock pins into, into the setup information section.

![alt text](https://cdn.sparkfun.com/assets/learn_tutorials/4/2/4/header_pinout.jpg "RaspberryPi Pin Layout")

