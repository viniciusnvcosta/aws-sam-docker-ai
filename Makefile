SHELL := /bin/bash

# Import variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Ensure mandatory environment variables are set
ifndef REGION
$(error REGION is not set in .env)
endif

ifndef ECR_REPO_NAME
$(error ECR_REPO_NAME is not set in .env)
endif

ifndef IMAGE_TAG
$(error IMAGE_TAG is not set in .env)
endif

ifndef STACK_NAME
$(error STACK_NAME is not set in .env)
endif

ifndef S3_BUCKET_NAME
$(error S3_BUCKET_NAME is not set in .env)
endif

# Variables definitions
# -----------------------------------------------------------------------------

ifeq ($(TIMEOUT),)
TIMEOUT := 60
endif

ifeq ($(MODEL_PATH),)
MODEL_PATH := ./ml/model/
endif

ifeq ($(MODEL_NAME),)
MODEL_NAME := model.pkl
endif

ACCOUNT_ID = $(shell aws sts get-caller-identity --query "Account" --output text)
ECR_URI = $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/$(ECR_REPO_NAME):$(IMAGE_TAG)

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: help all install run build validate test-local-invoke test-local-api sync create-ecr-repo ecr-login deploy test compose down generate_dot_env

all: install build validate test-local-invoke sync deploy

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install           Install dependencies"
	@echo "  run               Run the application"
	@echo "  build             Build the SAM application"
	@echo "  validate          Validate the SAM template"
	@echo "  test-local-invoke Test locally with invoke function directly"
	@echo "  test-local-api    Test locally with an API"
	@echo "  sync              Sync the SAM application with the AWS CloudFormation stack"
	@echo "  create-ecr-repo   Create ECR repository"
	@echo "  ecr-login         Login to ECR"
	@echo "  deploy            Deploy the SAM application"
	@echo "  test              Run tests"
	@echo "  compose           Run docker-compose"
	@echo "  down              Stop docker-compose"
	@echo "  generate_dot_env  Generate .env file"
	@echo "  clean             Clean up"

install: generate_dot_env
	pip install --upgrade pip
	poetry install --with dev --sync

run:
	PYTHONPATH=app/ poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Build the SAM application
.PHONY: build
build:

	@echo "Building the SAM application..."
	sam build --cached --parallel --debug

# Validate the SAM template
.PHONY: validate
validate:
	@echo "Validating the SAM template..."
	sam validate --lint --debug

# Test locally with invoke function directly
.PHONY: test-local-invoke
test-local-invoke:
	@echo "Invoking function locally..."
	sam local invoke "InferenceFunction" --event events/event.json

# Test locally with an API
.PHONY: test-local-api
test-local-api:
	@echo "Starting local API..."
	sam local start-api

# Sync the SAM application with the AWS CloudFormation stack
.PHONY: sync
sync:
	@echo "Syncing the SAM application..."
	sam sync --stack-name $(STACK_NAME) --watch

# Create ECR repository
.PHONY: create-ecr-repo
create-ecr-repo:
	@echo "Creating ECR repository..."
	aws ecr create-repository --repository-name $(ECR_REPO_NAME) --image-scanning-configuration scanOnPush=true --region $(REGION) || true

# Login to ECR
.PHONY: ecr-login
ecr-login:
	@echo "Logging in to ECR..."
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com

# Deploy the SAM application
.PHONY: deploy
deploy: create-ecr-repo ecr-login
	@echo "Deploying the SAM application..."

pytest:
	poetry run pytest tests -vv --show-capture=all

compose: generate_dot_env
	docker-compose build
	docker-compose up -d

down:
	docker-compose down

generate_dot_env:
	@if [[ ! -e .env ]]; then \
		cp .env.example .env; \
	fi

# Clean up
.PHONY: clean
clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .aws-sam
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build