all:
	./simulator.py | column -s, -t

pylint:
	pylint --rcfile=pylint.rc *.py | less -S
