SHELL := /bin/bash # Use bash syntax

## Make sure any required env-var's are set (i.e with guard-STACK_NAME)
guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "ERROR: Required environment variable is $* not set!"; \
        exit 1; \
    fi

## Make sure any macro's the stack needs are created/updated
update-macro-template:
	aws cloudformation deploy \
		--stack-name CFN-StringMacros \
		--template-file cloudformation/single-deploy-string-macros.yml \
		--capabilities CAPABILITY_IAM

## Make sure the ECR all SearchAPI's share is up to date
# stack-name ECR first, so it doesn't match SearchAPI-* stacks
update-searchapi-ecr:
	aws cloudformation deploy \
		--stack-name ECR-SearchAPI \
		--template-file cloudformation/single-deploy-ecr.yml

## Update that registry with a container
docker-update-ecr: guard-BRANCH
	export DOCKER_ECR=$$(aws cloudformation describe-stacks \
					--stack-name "ECR-SearchAPI" \
					--query "Stacks[?StackName=='ECR-SearchAPI'].Outputs[0][?OutputKey=='RegistryUri'].OutputValue" \
					--output=text) && \
	([ -n "$${DOCKER_ECR}" ] || (echo "ERROR: Couldn't query aws stack" && exit -1)) && \
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$${DOCKER_ECR}" && \
	docker build -t "$${DOCKER_ECR}:$${BRANCH}" . && \
	docker push "$${DOCKER_ECR}:$${BRANCH}"

## Finally deploy the main stack
#	In --stack-name, after BRANCH, will replace all non-alpha chars with '-'
update-main-stack-template: guard-BRANCH
	aws cloudformation deploy \
		--stack-name "SearchAPI-$${BRANCH//[^[:alnum:]]/-}" \
		--template-file cloudformation/SearchAPI-stack.yml \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			GitHubBranch=${BRANCH} \
			Maturity=devel

## Main workflow for deploying a API Stack:
all: update-macro-template update-searchapi-ecr docker-update-ecr update-main-stack-template

## Delete the SearchAPI stack
delete: guard-BRANCH
	# Delete it:
	aws cloudformation delete-stack \
		--stack-name "SearchAPI-$${BRANCH//[^[:alnum:]]/-}"
	# Wait for delete to complete (And throw if delete failed):
	aws cloudformation wait stack-delete-complete \
		--stack-name "SearchAPI-$${BRANCH//[^[:alnum:]]/-}"
