.PHONY: all clean test

all: test

clean:
	rm -rf ./dist ./build ./*.egg-info

test:
	python -m compileall wcpan
	python -m unittest
