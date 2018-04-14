init:
	pip3 install -r requirements.txt

test:
	python test.py

clean:
	rm *.pyc

all:
	pip3 install -r requirements.txt
	python test.py