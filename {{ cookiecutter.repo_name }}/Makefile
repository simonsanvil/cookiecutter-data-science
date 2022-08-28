.PHONY: environment clean data lint requirements sync_to_cloud sync_from_cloud release docs

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = {{ cookiecutter.python_package }}
PYTHON_INTERPRETER = python3
PDOC_TEMPLATE_DIR = docs/pdoc_template
ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif
include .env
DOCS_CREATED = $(shell [ -d docs/{{ cookiecutter.python_package }} ] && echo True || echo False)
RED='\033[0;31m'
NC='\033[0m' # No Color
GREEN='\033[0;32m'
YELLOW='\033[0;33m'

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Set up python interpreter environment
environment:
ifeq (True,$(HAS_CONDA))
		@echo ">>> ${GREEN}Detected conda, creating conda environment.${NC}"
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m venv ./.venv
	@echo ">>> New virtualenv created. Activate with:\nsource .venv/bin/activate
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) src/tests/test_environment.py

## Install Python Dependencies
requirements: test_environment
	pip install -U pip setuptools wheel
	pip install -r requirements.txt

## Make Dataset
data: requirements
	$(PYTHON_INTERPRETER) src//data/make_dataset.py data/raw data/processed

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Make the documentation with pdoc3
docs:
	pdoc3 --html -o docs --template-dir $(PDOC_TEMPLATE_DIR) --force src/{{ cookiecutter.python_package }}

## Serve the documentation to localhost:8000
serve_docs: docs
	@echo ">>> ${GREEN}Serving {{ cookiecutter.python_package }} docs at http://localhost:8000${NC}"
	python -m http.server -d docs/{{ cookiecutter.python_package }}

	
## Push {{ cookiecutter.python_package }} release
release:
	$(info "Pushing {{ cookiecutter.python_package }} release")
	python dev_tools/make_release.py

{% if cookiecutter.cloud_provider != '' -%}
## Upload Data to cloud storage
sync_to_cloud:
	$(info "Uploading data to cloud storage")
	{% if cookiecutter.cloud_provider == 'aws' -%}
	ifeq (default,$(AWS_PROFILE,default))
		aws s3 sync data/ s3://$(AWS_BUCKET)/data/
	else
		aws s3 sync data/ s3://$(AWS_BUCKET)/data/ --profile $(AWS_PROFILE)
	endif
	{% elif cookiecutter.cloud_provider == 'gcp' -%}
	gsutil -m cp -r data/ gs://$(GCP_BUCKET)/data/
	{% elif cookiecutter.cloud_provider == 'azure' -%}
	az storage blob directory upload -c $(AZURE_STORAGE_CONTAINER) -s data/ -d data/ --recursive
	{%- endif %}
	
## Download Data from cloud storage
sync_from_cloud:
	$(info "Downloading data from cloud storage")
	{% if cookiecutter.cloud_provider == 'aws' -%}
	ifeq (default,$(AWS_PROFILE,default))
		aws s3 sync s3://$(AWS_BUCKET)/data/ data/
	else
		aws s3 sync s3://$(AWS_BUCKET)/data/ data/ --profile $(AWS_PROFILE)
	endif
	{% elif cookiecutter.cloud_provider == 'gcp' -%}
	gsutil -m cp -r gs://$(GCP_BUCKET)/data/ data/
	{% elif cookiecutter.cloud_provider == 'azure' -%}
	az storage blob directory download -c $(AZURE_STORAGE_CONTAINER) -s data/ -d data/ --recursive
	{%- endif %}
{% endif %}

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')

