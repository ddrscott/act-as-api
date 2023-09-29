DOCKER_IMAGE ?= $(shell basename $(CURDIR))
PORT ?= 8000
DOCKER_RUN ?= docker run --rm -it \
			  -e OPENAI_API_KEY \
              -e PORT \
              -e AUTH0_DOMAIN \
              -e AUTH0_AUDIENCE \
              -e CLIENT_ORIGIN_URL \
			  -v $(CURDIR):/app \
			  -w /app -p $(PORT):$(PORT) $(DOCKER_IMAGE)

docker-run: docker-build
	$(DOCKER_RUN)

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-shell: docker-build
	$(DOCKER_RUN) /bin/bash

requirements.lock: requirements.txt
	pip freeze > $@
