all:
	bin/debops-update

clean:
	rm -rf $$HOME/.local/share/debops
	sudo rm -rf /usr/local/bin/debops*

install:
	bin/debops-update

syntax:
	find bin -type f -exec bash -n {} \;

.PHONY: all clean install syntax
