all: sdist egg register

sdist:
	python2.4 setup.py sdist upload

register:
	python2.4 setup.py register

egg:
	python2.4 setup.py bdist_egg upload
	python2.5 setup.py bdist_egg upload
