lint: ## Lint whole python project
	@echo "Run linter ds_rewards_selector and tests folders"
	flake8 gptpedia/ tests/
	isort --check-only --diff --stdout .
	@echo "Done"

format: ## Format python code
	isort .

install: ## Create virtual environment and setup requirements
	@echo "Setup poetry virtual environment"
	poetry install
	@echo "Done"

activate_virtual_env: ## Activate virtual environment
	@echo "Activating poetry virtual environment"
	poetry shell
	@echo "Done"

test: ## Run test suit
	@echo "Running tests..."
	pytest tests --cov=gptpedia
	@echo "Done test run"

test_cov: ## Run test suit
	@echo "Running tests..."
	pytest tests --cov=gptpedia --cov-report=html
	@echo "Done test run"

