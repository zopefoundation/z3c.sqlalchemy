all: doc

doc: pdf html

clean:
	find ${PWD} -name \*pyc -exec rm {} \;
	find ${PWD} -name \*pyo -exec rm {} \;

pdf: clean
	epydoc --graph=all --pdf -o doc ${PWD}

html: clean 
	epydoc --graph=all  --html -o doc ${PWD}
