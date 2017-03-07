#!/bin/bash

TMPDIR="/tmp/"
ELASTIC_SEARCH_VERSION="2.3.4"

update_upgrade(){
	sudo apt-get -y update && sudo apt-get -y upgrade
	return 0
}

install_python(){
	sudo apt-get -y install python
	sudo apt-get -y install python-pip
	sudo -H pip install --upgrade pip
	sudo -H pip install requests
	return 0
}

install_java(){
	sudo echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | sudo tee /etc/apt/sources.list.d/webupd8team-java.list
	sudo echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | sudo tee -a /etc/apt/sources.list.d/webupd8team-java.list
	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
	sudo apt-get update
	sudo apt-get -y install oracle-java8-installer
	return 0
}

install_elasticsearch(){
	cd $TMPDIR
	wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-$ELASTIC_SEARCH_VERSION.deb
	sudo dpkg -i elasticsearch-$ELASTIC_SEARCH_VERSION.deb
	return 0
}

enable_elasticsearch_start(){
	sudo update-rc.d elasticsearch defaults
	return 0
}

install_hq(){
	cd /usr/share/elasticsearch/bin
	sudo ./plugin install royrusso/elasticsearch-HQ
	return 0
}

update_upgrade

install_python

install_java

install_elasticsearch

enable_elasticsearch_start

install_hq
