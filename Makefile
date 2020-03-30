.PHONY: pypi, tag, shell, typecheck, pytest, test

pypi:
	poetry publish --build
	make tag

tag:
	git tag $$(python -c "from hypothesis_grammar import __version__; print(__version__)")
	git push --tags

shell:
	PYTHONPATH=hypothesis_grammar:tests:$$PYTHONPATH ipython

typecheck:
	pytype hypothesis_grammar

pytest:
	py.test -v -s --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb tests/

test:
	$(MAKE) typecheck
	$(MAKE) pytest
