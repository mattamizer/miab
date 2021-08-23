createenv:
	python -m venv venv

install: createenv
		. venv/bin/activate && pip install -r requirements.txt

run:
	docker-compose up -d && FLASK_APP=app.py FLASK_ENV=development flask run

stop:
	docker-compose down

test: run
	python -m unittest tests/*.py -v

clean: stop
	rm -rf venv
