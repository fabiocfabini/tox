# Set default target
.DEFAULT_GOAL := help

# Get current dir
dir = $(shell pwd)

# Current vms dir
vm=$(dir)/vm/vms

install:
	@echo "Installing vms..."
	cp $(vm) /usr/local/bin/vms
	@echo "Installing package tox..."
	pip install -e .
	@echo "Done."

help:
	@echo "Usage: make [install|help]"
	@echo "install: install vms in /usr/local/bin and tox in current python enviroment"
	@echo "help: 	 show this help"