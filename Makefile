init:
	pip3 install -r requirements.txt

test:
	python test.py

clean:
	rm -f *.pyc
	rm -rf __pycache__/

all:
	pip3 install -r requirements.txt
	python test.py