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

# Variables
ACCOUNT_ID = $(shell aws sts get-caller-identity --query "Account" --output text)
ECR_URI = $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/$(ECR_REPO_NAME):$(IMAGE_TAG)

# Default target
.PHONY: all
all: build validate test-local-invoke sync deploy

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

# Test locally without an API (invoke function directly)
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

# Clean up generated files
.PHONY: clean
clean:
	@echo "Cleaning up generated files..."
	rm -rf .aws-sam
	# rm -f packaged.yaml
