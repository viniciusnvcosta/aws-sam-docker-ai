# Import variables from .env file
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Variables
ECR_URI = $(shell aws sts get-caller-identity --query "Account" --output text).dkr.ecr.$(REGION).amazonaws.com/$(ECR_REPO_NAME):$(IMAGE_TAG)

# Default target
.PHONY: all
all: build validate test-local-invoke sync deploy

# Build the SAM application
.PHONY: build
build:
	sam build --cached --parallel --use-container --debug

# Validate the SAM template
.PHONY: validate
validate:
	sam validate --lint --debug

# Test locally without an API (invoke function directly)
.PHONY: test-local-invoke
test-local-invoke:
	sam local invoke "InferenceFunction" --event events/event.json

# Test locally with an API
.PHONY: test-local-api
test-local-api:
	sam local start-api

# Sync the SAM application with the AWS CloudFormation stack
.PHONY: sync
sync:
	sam sync --stack-name $(STACK_NAME) --watch

# Create ECR repository
.PHONY: create-ecr-repo
create-ecr-repo:
	aws ecr create-repository --repository-name $(ECR_REPO_NAME) --image-scanning-configuration scanOnPush=true --region $(REGION) || true

# Login to ECR
.PHONY: ecr-login
ecr-login:
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(shell aws sts get-caller-identity --query "Account" --output text).dkr.ecr.$(REGION).amazonaws.com

# Deploy the SAM application
.PHONY: deploy
deploy: create-ecr-repo ecr-login
	# sam package --s3-bucket $(S3_BUCKET_NAME) --output-template-file packaged.yaml
	sam deploy --template-file template.yaml --stack-name $(STACK_NAME) --capabilities CAPABILITY_IAM --s3-bucket $(S3_BUCKET_NAME) --image-repository $(ECR_URI) --region $(REGION)

# Clean up generated files
.PHONY: clean
clean:
	rm -rf .aws-sam
	# rm -f packaged.yaml
