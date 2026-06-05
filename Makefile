.PHONY: test
test:
	python retrieve-twitter/retrieve-twitter.py

.PHONY: stop
stop:	
	docker kill $(docker ps -q)

.PHONY: reset
reset:	
	docker compose down --volumes --rmi all

.PHONY: build
build:	
	docker compose up -d --build

.PHONY: web
web:	
	docker compose up airflow-webserver --build 

.PHONY: triggerer
triggerer:	
	docker compose up airflow-triggerer --build

.PHONY: worker
triggerer:	
	docker compose up airflow-worker --build

.PHONY: nginx
nginx:	
	docker compose up nginx -d --build 

.PHONY: init
init:	
	docker compose up airflow-init
	