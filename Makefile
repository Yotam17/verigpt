.PHONY: build run stop clean logs

# Build the Docker image
build:
	docker build -t verigpt .

# Run the container
run:
	docker run -d --name verigpt --env-file .env verigpt

# Run with docker-compose
up:
	docker-compose up -d

# Stop the container
stop:
	docker stop verigpt || true
	docker rm verigpt || true

# Stop with docker-compose
down:
	docker-compose down

# View logs
logs:
	docker logs -f verigpt

# Clean up
clean:
	docker system prune -f
	docker image prune -f

# Interactive shell
shell:
	docker run -it --rm verigpt /bin/bash
