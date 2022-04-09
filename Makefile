PROJECT_NAME ?= telegram
REGISTRY = registry.miem.hse.ru/301
PROJECT_NAMESPACE ?= conference
REGISTRY_IMAGE ?= $(REGISTRY)/$(PROJECT_NAMESPACE)/$(PROJECT_NAME)

all:
	@echo "make clean              - Remove files created by distutils"
# 	@echo "make devenv             - Create & setup development virtual environment"
# 	@echo "make lint               - Check code with pylama"
# 	@echo "make test               - Run tests"
# 	@echo "make cov                - Run tests and generate coverage html report"
	@echo "=== TESTING ==="
	@echo "    make build-testing      - Build a docker image with tag 'testing'"
	@echo "    make upload-testing     - Build and upload a docker image with tag 'testing' to the registry"
	@echo "    make prov-testing       - Load files needed to start the app to the preprod server with scp"
	@echo "    make up-testing         - Start app in preproduction environment (use on server)"
	@echo "    make up-testing-d       - Start app in preproduction environment (use on server) and detach"
	@echo ""
	@echo "=== PRODUCTION ==="
	@echo "    make build-prod         - Build a docker image with tag 'latest'"
	@echo "    make upload-prod        - Build and upload a docker image with tag 'latest' to the registry"
	@echo "    make prov-prod          - Load files needed to start the app to the prod server with scp"
	@echo "    make up-prod            - Start app in production environment (use on server)"
	@echo "    make up-prod-d          - Start app in production environment (use on server) and detach"
# 	@echo "Use flag -i to ignore errors (e.g. by pylama)"
	@exit 0

clean:
	rm -rf *.egg-info dist

# devenv: clean
# 	rm -rf env
# 	python3 -m venv env
# 	# these two lines are for Linux
# 	env/bin/pip install -U pip
# 	env/bin/pip install -Ue './lib/database/.[dev]'
# 	env/bin/pip install -Ue './api/.[dev]'
# 	env/bin/pip install -Ur './telegram_bot/requirements.txt'
# 	env/bin/pip install -Ue './zulip_bot/.[dev]'
# 	env/bin/pip install -Ur './scheduler/requirements.txt'

# lint:
# 	pylama
#
# test:
# 	coverage run -m pytest
#
# cov: test
# 	coverage html

# TESTING
build-testing:
	docker build -t $(REGISTRY_IMAGE):testing .

upload-testing: build-testing
	docker push $(REGISTRY_IMAGE):testing

prov-testing:
	scp -r .env Makefile data/ docker-compose.preprod.yml p301-test@preprod.conf.konstant-anxiety.ru:/home/p301-test/conf_app/

pull-testing:
	sudo docker-compose -f docker-compose.preprod.yml pull

up-testing: pull-testing
	sudo docker-compose -f docker-compose.preprod.yml up --force-recreate --remove-orphans

up-testing-d: pull-testing
	sudo docker-compose -f docker-compose.preprod.yml up -d --force-recreate --remove-orphans


# PRODUCTION
build-prod:
	docker build -t $(REGISTRY_IMAGE):latest .

upload-prod: build-prod
	docker push $(REGISTRY_IMAGE):latest

prov-prod:
	scp -r .env Makefile data/ docker-compose.prod.yml p301@conf.konstant-anxiety.ru:/home/p301-test/conf_app/

pull-prod:
	sudo docker-compose -f docker-compose.prod.yml pull

up-prod: pull-prod
	sudo docker-compose -f docker-compose.prod.yml up --force-recreate --remove-orphans

up-prod-d: pull-prod
	sudo docker-compose -f docker-compose.prod.yml up -d --force-recreate --remove-orphans
