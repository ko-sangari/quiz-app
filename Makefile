
coffee:
	@printf 'Be Happy Even if Things Aren’t Perfect Now. 🎉🎉🎉\n'
	@printf 'Enjoy your coffee! ☕\n'

dev:
	@docker compose -f docker-compose.yaml up --build

run:
	@docker compose -f docker-compose.yaml up --build -d

down:
	@docker compose -f ./docker-compose.yaml down --remove-orphans

shell:
	@docker exec -it fastapi_service bash

tests:
	@docker exec -it fastapi_service poetry run pytest

coverage:
	@docker exec -it fastapi_service poetry run coverage run -m pytest
	@docker exec -it fastapi_service poetry run coverage report

mypy:
	@docker exec -it fastapi_service poetry run mypy --config-file mypy.ini --explicit-package-bases .

.PHONY: coffee dev run down shell tests coverage mypy
