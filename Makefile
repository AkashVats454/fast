run:
	uvicorn main:app --reload

install:
	pip install -r requirements.txt

build:
	python setup.py build bdist_wheel

clean:
	if exist "./build" rd /s /d build
	if exist "./dist" rd /s /d dist
	if exist "./postGresPackage.egg-info" rd /s /d postGresPackage.egg-info