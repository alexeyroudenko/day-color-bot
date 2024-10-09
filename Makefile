.PHONY: test
test:
	python tags.py

.PHONY: bot
bot:	
	python bot.py

.PHONY: run
run:	
	python app.py