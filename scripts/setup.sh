#! /bin/bash

# Show errors
function catch_errors() {
   echo "Error";
}

trap catch_errors ERR;

# Make sure only root can run the script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Global variables
HOME_PI="/home/pi"

echo "Installing git..."
apt-get install git

echo "Cloning repositories from http://github.com/jdcallet/ExeaInternetRadio..."
cd $HOME_PI
git clone http://github.com/jdcallet/ExeaInternetRadio

# Verify that git works fine
rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

curl -s https://syncthing.net/release-key.txt | sudo apt-key add -
echo "deb http://apt.syncthing.net/ syncthing stable" | sudo tee /etc/apt/sources.list.d/syncthing.list

echo "Updating system..."
apt-get -y update

echo "Installing some tools..."
apt-get install -y python-dev python-setuptools python-pip mpg123 syncthing lirc liblircclient-dev oracle-java8-jdk

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

pip install rpi.gpio

echo "Copying files for automatic initialization of syncthing..."
cp $HOME_PI/ExeaInternetRadio/scripts/syncthing /etc/init.d/

chmod +x /etc/init.d/syncthing
update-rc.d syncthing defaults

echo "Copying files for automatic initialization of software..."
cp $HOME_PI/ExeaInternetRadio/scripts/player /etc/init.d/

echo "Copying files for check sound..."
cp $HOME_PI/ExeaInternetRadio/scripts/checkSound.sh /usr/bin/

# Verify command
rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

# Permisions of the file
chmod +x /etc/init.d/player
update-rc.d player defaults
chmod +x /usr/bin/checkSound.sh
(crontab -l 2>/dev/null; echo "@reboot sudo /usr/bin/checkSound.sh") | crontab -

echo "Installing remote-iot..."
cd $HOME_PI/ExeaInternetRadio/
curl -s -L https://remote-iot.com/install/remote-iot-install.sh | sudo -s bash
/etc/remote-iot/services/setup.sh

echo "Installing Termcolor..."
cd $HOME_PI/ExeaInternetRadio/lib/termcolor-1.1.0
./setup.py install

echo "Creating Music directory..."
mkdir $HOME_PI/Music

chown -Rf pi $HOME_PI/*

echo "Finishing setup"
