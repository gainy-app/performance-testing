export PARAMS ?= $(filter-out $@,$(MAKECMDGOALS))

-include .env
-include .env.local

up:
	touch .env.local
	docker-compose up --scale worker=${WORKER_NODES}

down:
	docker-compose down

clean:
	docker-compose down --rmi local -v --remove-orphans

style-check:
	yapf --diff -r src/

style-fix:
	yapf -i -r src/

%:
	@:
