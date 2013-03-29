default:
	@echo 'Please use `make app` or `make clean`'

app:
	if [ -f setup.py ]; then rm setup.py; fi
	py2applet --make-setup akintu.py
	python setup.py py2app -r data,res

clean:
	rm -rf res/saves res/ip_history.txt build dist __pycache__
