#!/bin/bash


TMPDIR="/tmp/"
SSDEEP_VERSION="2.13"
YARA_VERSION="3.4.0"
YARA_PYTHON_VERSION="3.4.0"
CUCKOO_INSTALL_LOCATION="/etc"
TESSERACT_LANGS="eng nld"
LIBVIRT_VERSION="1.3.5"
CUCKOO_CURRENT=FALSE
CUCKOO_COMMIT="9d16025d5e6b264ce8db3aeccfc37b3dcedb7f43"
PRIMARY_INTERFACE="ens160"
SECONDARY_INTERFACE="ens192"

check_sudo(){
	if [ "$(id -u)" != "0" ]; then
		printf "This script must be run as root.\n"
		exit 1
	fi
}

update_upgrade(){
	sudo apt-get -y update && sudo apt-get -y upgrade
	return 0
}

install_dependencies(){
	sudo apt-get -y install git python python-dev python-pip python-m2crypto libmagic1 swig libvirt-dev upx-ucl libssl-dev geoip-database libgeoip-dev libjpeg-dev mono-utils libfuzzy-dev exiftool python-sqlalchemy mongodb python-bson python-dpkt python-jinja2 python-magic python-gridfs python-libvirt python-bottle python-pefile python-chardet build-essential autoconf automake libtool dh-autoreconf libcurl4-gnutls-dev libmagic-dev dkms python-pyrex python-dateutil supervisor libxml2-dev libxslt1-dev libffi-dev python-pymongo libjansson-dev unzip
	return 0
}

install_pip_dependencies(){
	sudo -H pip install --upgrade pip
	sudo -H pip install sqlalchemy jinja2 markupsafe libvirt-python pymongo bottle pefile django chardet pygal clamd django-ratelimit pycrypto rarfile jsbeautifier dpkt nose dnspython pytz requests python-magic geoip pillow java-random python-whois git+https://github.com/crackinglandia/pype32.git pydeep maec py3compat lxml cybox distorm3 flask 
	sudo -H pip install -U dpkt
	sudo -H pip install --upgrade ndg-httpsclient
	return 0
}

install_tcpdump(){
	sudo apt-get -y install tcpdump libcap2-bin
	sudo chmod +s /usr/sbin/tcpdump
	chmod +s /usr/sbin/tcpdump
	sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
	sudo getcap /usr/sbin/tcpdump
	return 0
}

install_pydeep_ssdeep(){
	cd $TMPDIR
	wget -O ssdeep-$SSDEEP_VERSION.tar.gz http://downloads.sourceforge.net/project/ssdeep/ssdeep-$SSDEEP_VERSION/ssdeep-$SSDEEP_VERSION.tar.gz
	tar xvfz ssdeep-$SSDEEP_VERSION.tar.gz
	cd ssdeep-$SSDEEP_VERSION
	./configure --prefix=/usr
	make
	make check
	make install
	sudo -H pip install git+https://github.com/kbandla/pydeep.git
	cd $TMPDIR
	return 0
}

install_volatility(){
	sudo apt-get -y install python-pil
	sudo -H pip install openpyxl
	sudo -H pip install git+https://github.com/volatilityfoundation/volatility.git
	return 0
}

install_suricata(){
	sudo add-apt-repository ppa:oisf/suricata-beta
	sudo apt-get update
	sudo apt-get -y install suricata
	touch /etc/suricata/threshold.config
	return 0
}

install_ids_updater(){
	cd $TMPDIR
	sudo git clone https://github.com/seanthegeek/etupdate.git
	sudo cp etupdate/etupdate /usr/sbin
	sudo /usr/sbin/etupdate -V
	return 0
}

install_yara(){
	cd $TMPDIR
	apt-get -y install libpcre3 libpcre3-dev
	wget -O yara$YARA_VERSION.tar.gz https://github.com/plusvic/yara/archive/v$YARA_VERSION.tar.gz
	tar xvfz yara$YARA_VERSION.tar.gz
	cd yara-$YARA_VERSION
	./bootstrap.sh
	./configure --with-crypto --enable-cuckoo --enable-magic
	make
	make check
	make install
	cd $TMPDIR
	return 0
}

install_yara_python(){
	cd $TMPDIR
	wget -O yara-python-$YARA_PYTHON_VERSION.tar.gz https://github.com/plusvic/yara-python/archive/v$YARA_PYTHON_VERSION.tar.gz
	tar xvfz yara-python-$YARA_PYTHON_VERSION.tar.gz
	cd yara-python-$YARA_PYTHON_VERSION
	sudo python setup.py build
	sudo python setup.py install
	return 0
}

install_cuckoo(){
	if [ $CUCKOO_CURRENT = "TRUE" ]; then
		git clone https://github.com/cuckoosandbox/cuckoo $CUCKOO_INSTALL_LOCATION/cuckoo
	else 
		git clone https://github.com/cuckoosandbox/cuckoo $CUCKOO_INSTALL_LOCATION/cuckoo
		cd $CUCKOO_INSTALL_LOCATION/cuckoo
		git reset --hard $CUCKOO_COMMIT
	fi
	
	cd $CUCKOO_INSTALL_LOCATION/cuckoo
	sudo -H pip install -r requirements.txt
	sudo python utils/community.py -wafb monitor
	sudo python utils/community.py -wafb 2.0
	sudo python utils/community.py --signatures --force
	sudo python utils/community.py -a
	return 0
}


install_tesseract(){
	sudo apt-get -y install tesseract-ocr
	for LANG in $TESSERACT_LANGS
		do
			sudo apt-get install tesseract-ocr-$LANG
		done
	return 0
}

install_libvirt(){
	sudo apt-get -y install libpciaccess-dev pkg-config libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev libdevmapper-dev libnl-3-dev libnl-route-3-dev libnl-genl-3-dev uuid-dev
	cd $TMPDIR
	wget http://libvirt.org/sources/libvirt-$LIBVIRT_VERSION.tar.gz
	tar zxf libvirt-$LIBVIRT_VERSION.tar.gz libvirt-$LIBVIRT_VERSION
	cd libvirt-$LIBVIRT_VERSION/
	./configure --with-esx=yes
	make
	sudo make install
	return 0
}

install_dhcp_server(){
	sudo apt-get install -y isc-dhcp-server
	return 0
}

check_sudo

update_upgrade

install_dependencies

install_pip_dependencies

install_suricata

install_ids_updater

install_tcpdump

install_pydeep_ssdeep

install_volatility

install_yara

install_yara_python

install_tesseract

install_dhcp_server

install_libvirt

install_cuckoo
