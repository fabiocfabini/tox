# Set default target
.DEFAULT_GOAL := help

# Get current dir
dir = $(shell pwd)

# Current vms dir
vm=$(dir)/vm/vms

install:
	@echo "Installing..."
	cp $(vm) /usr/local/bin/vms
	@echo "Done."

help:
	@echo "Usage: make [install|help]"
	@echo "install: install vms in /usr/local/bin"
	@echo "help: 	 show this help"