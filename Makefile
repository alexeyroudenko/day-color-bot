.PHONY: test
test:
	python retrieve-twitter/retrieve-twitter.py

.PHONY: run
run:	
	python twimg/twimg.py

.PHONY: build
build:
	docker compose up -d --build	