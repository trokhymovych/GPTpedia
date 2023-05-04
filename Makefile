lint: ## Lint whole python project
	@echo "Run linter ds_rewards_selector and tests folders"
	flake8 wikigpt/
	isort --check-only --diff --stdout .
	@echo "Done"

format: ## Format python code
	isort .

create_virtual_env: ## Create virtual environment and setup requirements
	@echo "Creating poetry virtual environment"
	virtualenv -p python venv
	source venv/bin/activate
	pip install -r requirements.txt
	@echo "Done"

activate_virtual_env: ## Activate virtual environment
	@echo "Activating poetry virtual environment"
	source venv/bin/activate
	@echo "Done"
