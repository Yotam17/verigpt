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
		echo "Please run: make setup-env"; \
		exit 1; \
	else \
		echo "✅ .env file found"; \
		echo "Checking environment variables..."; \
		@if grep -q "your-openai-api-key-here" .env; then \
			echo "⚠️  WARNING: OPENAI_API_KEY still has default value!"; \
			echo "   Please edit .env and set your actual API key"; \
		else \
			echo "✅ OPENAI_API_KEY appears to be set"; \
		fi; \
	fi

# Test environment variables
test-env:
	@echo "🧪 Testing environment variables..."
	@python -m app.verigpt_agent --test-env

# Setup environment (copy example and prompt user)
setup-env:
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env from env.example"; \
		echo "⚠️  IMPORTANT: Please edit .env and add your actual OpenAI API key"; \
		echo "   Replace 'your-openai-api-key-here' with your real API key"; \
		echo "   Then run: make check-env"; \
	else \
		echo "✅ .env file already exists"; \
		echo "Checking if it needs updates..."; \
		@if grep -q "your-openai-api-key-here" .env; then \
			echo "⚠️  WARNING: .env still contains default values!"; \
			echo "   Please update with your actual API key"; \
		else \
			echo "✅ .env appears to be properly configured"; \
		fi; \
	fi

# Security check - verify .env is not committed
security-check:
	@echo "🔒 Security check..."
	@if git ls-files | grep -q "\.env"; then \
		echo "❌ CRITICAL: .env file is tracked by git!"; \
		echo "   This is a security risk!"; \
		echo "   Remove it with: git rm --cached .env"; \
		exit 1; \
	else \
		echo "✅ .env file is not tracked by git (good!)"; \
	fi
	@if [ -f .env ]; then \
		if grep -q "your-openai-api-key-here" .env; then \
			echo "⚠️  WARNING: .env contains default values"; \
		else \
			echo "✅ .env contains custom values"; \
		fi; \
	else \
		echo "⚠️  .env file not found"; \
	fi

# Test file structure
test-structure:
	@echo "🧪 Testing file structure..."
	@python -m app.verigpt_agent --test-structure

# Test API service
test-api:
	@echo "🧪 Testing API service..."
	@python app/test_api.py

# Test API with Python script
test-api-python:
	@echo "🧪 Testing API with Python script..."
	@python app/test_api.py

# Show API documentation URLs
api-docs:
	@echo "📚 API Documentation:"
	@echo "   Swagger UI: http://localhost:8000/docs"
	@echo "   ReDoc: http://localhost:8000/redoc"
	@echo "   Health: http://localhost:8000/health"
