# What is the BeerScaleIOT
The BeerScaleIOT is an internet of things device that is used to collect data from scales collecting weight data of kegs to know the percentage of how full they are.

More information later

# How Does it Work
The program work in multiple parts
## Code on the Pi
There are two parts on the PI.
### Flask Application
Displays the server

### Scale Info Reader
Reads the information from the scale

# How to Build and Setup
## setting up the raspberry pi
Install An operating system on to the Pi. I used Raspian using NOOBS.
With a quick removal of the bloat ware that comes with the PI, everything should be ready.
Make sure that Flask is installed on the Pi.
```
sudo apt-get install flask
```
Download the RaspberryPiCode/FlaskApplication folder to the Pi. 
To start the FlaskMain.py script has to be run within the RaspberryPiCode/FlaskApplication folder.
You can test it to see if it works with the following commands.
```
chmod +x FlaskMain.py
./FlaskMain.py
```
Create a file called StartFlaskApp.sh in the BeerScaleIOT/RaspberryPiCode/FlaskApplication/ floder:
```
#!/bin/bash
cd /home/pi/Documents/BeerScaleIOT/RaspberryPiCode/FlaskApplication/
chmod +x FlaskMain.py
./FlaskMain.py
```
Run the following command to create the exacutable from the new file and test it to see if it works.
```
chmod +x StartFlaskApp.sh
./StartFlaskApp.sh
```
For the Prgram to start on startup of the Pi you will need to add the following line to the file at /etc/rc.local.
```
/home/pi/Documents/BeerScaleIOT/RaspberryPiCode/FlaskApplication/StartFlaskApp.sh
```
Restart the Pi to see if it worked.
Use the following command to get the IP of Flask Url
```
ipconfig
```
In my case, the IP is 192.168.0.57, so the Url is 192.168.0.57:5000
