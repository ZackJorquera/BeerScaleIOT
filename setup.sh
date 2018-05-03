#!/usr/bin/env bash

echo "Creating CFG"
echo "(cd RaspberryPiCode/Tools/; python ConfigReaderWriter.py)"
(cd RaspberryPiCode/Tools/; python ConfigReaderWriter.py)

echo "Building QuickPulse.c"
echo "gcc -shared -I/usr/include/python2.7 -lpython2.7 RaspberryPiCode/Tools/QuickPulse.c -o RaspberryPiCode/Tools/QuickPulse.so -l bcm2835"
gcc -shared -I/usr/include/python2.7 -lpython2.7 RaspberryPiCode/Tools/QuickPulse.c -o RaspberryPiCode/Tools/QuickPulse.so -l bcm2835

echo "Creating Aliases"
echo "echo \"alias startflaskapp=\"(cd `pwd`/RaspberryPiCode/FlaskApplication/; python FlaskMain.py)\"\" >> ~/.bashrc"
echo "alias startflaskapp=\"(cd `pwd`/RaspberryPiCode/FlaskApplication/; python FlaskMain.py)\"" >> ~/.bashrc
echo "echo \"alias startscaleaggregator=\"(cd `pwd`/RaspberryPiCode/ScaleAggregator/; python ScaleAggregator.py)\"\" >> ~/.bashrc"
echo "alias startscaleaggregator=\"(cd `pwd`/RaspberryPiCode/ScaleAggregator/; python ScaleAggregator.py)\"" >> ~/.bashrc
echo ". ~/.bashrc"
. ~/.bashrc

echo "Adding to /etc/rc.local"
echo 'echo "startflaskapp" >> /etc/rc.local'
echo 'echo "startscaleaggregator" >> /etc/rc.local'
echo "startflaskapp" >> /etc/rc.local
echo "startscaleaggregator" >> /etc/rc.local

