init:
	pip3 install .
clean:
	rm -f *.pyc
	rm -rf __pycache__/

all:
	pip3 install -r requirements.txt
