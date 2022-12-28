.PHONY: run
run:
	@echo "Building and running application" && \
	docker-compose down --remove-orphans && \
	docker-compose up --build

.PHONY: test
test:
	@echo "Running pytest" && \
	pipenv run pytest -v
