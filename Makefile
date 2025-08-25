.PHONY: build run stop clean logs

# Build the Docker image
build:
	docker build -t verigpt .

# Run the container with .env file
run:
	docker run -d --name verigpt --env-file .env -p 8000:8000 verigpt

# Run with docker-compose (uses .env automatically)
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
	docker run -it --rm --env-file .env verigpt /bin/bash

# Check if .env exists
check-env:
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "Please copy env.example to .env and set your OpenAI API key:"; \
		echo "cp env.example .env"; \
		echo "Then edit .env and add your OPENAI_API_KEY"; \
		exit 1; \
	else \
		echo "✅ .env file found"; \
		echo "Make sure OPENAI_API_KEY is set in .env"; \
	fi

# Test environment variables
test-env:
	@echo "🧪 Testing environment variables..."
	@python verigpt_agent.py --test-env

# Setup environment (copy example and prompt user)
setup-env:
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env from env.example"; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
		echo "   Then run: make check-env"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Test the API service
test-api:
	@echo "🧪 Testing API service..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ API service not responding"

# Test API with Python script
test-api-python:
	@echo "🧪 Testing API service with Python..."
	@python test_api.py

# Show API endpoints
api-docs:
	@echo "📚 API Documentation available at:"
	@echo "   Swagger UI: http://localhost:8000/docs"
	@echo "   ReDoc: http://localhost:8000/redoc"
	@echo "   Health: http://localhost:8000/health"
