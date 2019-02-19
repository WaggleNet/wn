#!/usr/bin/env bash

# Set the installation folder if not set
: ${HOME=$(eval echo ~)};
: ${WN_PATH="$HOME/wagglenet-wn"};

# Stop execution if stuff goes wrong
set -e;

function init_venv
{
	if [ ! -d "./venv" ]; then
		echo "> Installing virtualenv...";
		virtualenv -p python3 venv > /dev/null;
	fi
	source ./venv/bin/activate;
	pip install -U -r requirements.txt > /dev/null;
}

function install_cmd
{
	chmod +x $WN_PATH/wn;
	if [ ! -f "/usr/local/bin/wn" ]; then
		echo "> Installing command wn. Might require your password.";
		sudo ln -s $WN_PATH/wn /usr/local/bin/wn;
	else
		echo "> wn command looks fine.";
	fi
}

function upgrade
{
	echo "> Upgrading wn. You might need to enter your Git password."
	git fetch --all;
	git reset --hard origin/master;
	echo "> Setting up the environment";
	init_venv;
	install_cmd;
	echo "> Done! We're all good."
}

function install
{
	echo "> Installing wn into your home directory."
	git clone https://github.com/WaggleNet/wn.git $WN_PATH;
	cd $WN_PATH;
	echo "> Setting up the environment";
	init_venv;
	install_cmd;
	echo "> Done! We're all good."
}


# =====MAIN FUNCTION=====

echo "===============================";
echo "| WaggleNet One-click Bringup |";
echo "===============================";
echo "";

# Check if something is already installed
if [ -d "$WN_PATH" ]; then
	echo "> You have installed this before.";
	cd $WN_PATH;
	echo "> We'll upgrade wn for you.";
	upgrade;
else 
	echo "> Welcome to WaggleNet! I'm going to install the One-click tool for you.";
	echo "  Onwards you can access WaggleNet's service stack using the following:";
	echo "        wn ";
	echo "> Starting installation procedure.";
	install;
fi



