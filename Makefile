SHELL := /bin/bash # Use bash syntax

## Make sure any required env-var's are set (i.e with guard-STACK_NAME)
guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "ERROR: Required environment variable is $* not set!"; \
        exit 1; \
    fi

#####################
## SINGLE DEPLOY'S ##
#####################

## Make sure any macro's the stack needs are created/updated
single-deploy-macro-template: guard-AWS_PROFILE
	aws --profile=$${AWS_PROFILE} cloudformation deploy \
			--stack-name 'CFN-StringMacros' \
			--template-file cloudformation/single-deploy-string-macros.yml \
			--capabilities CAPABILITY_IAM

## Make sure the ECR all SearchAPI's share is up to date
# stack-name ECR first, so it doesn't match SearchAPI-* stacks
single-deploy-searchapi-ecr: guard-AWS_PROFILE
	aws --profile=$${AWS_PROFILE} cloudformation deploy \
			--stack-name 'ECR-SearchAPI' \
			--template-file cloudformation/single-deploy-ecr.yml

## Deploy/update the minimal user, that can manage SearchAPI stacks
single-deploy-github-user: guard-AWS_PROFILE
	aws --profile=$${AWS_PROFILE} cloudformation deploy \
			--stack-name 'GitHub-SearchAPI-User' \
			--template-file cloudformation/single-deploy-github-user.yml \
			--capabilities CAPABILITY_NAMED_IAM

######################
## HELPER FUNCTIONS ##
######################

## Return the ecr uri, or error out if it can't be found.
# Use with `$(call get-ecr,AWS_ECR)`, which will populate "AWS_ECR"
# with the searchapi ECR URI.
define get-ecr
	$(1)=$$(aws cloudformation describe-stacks \
		--stack-name "ECR-SearchAPI" \
		--query "Stacks[?StackName=='ECR-SearchAPI'][].Outputs[?OutputKey=='RegistryUri'].OutputValue" \
		--output=text) && \
	([ -n "$${AWS_ECR}" ] || (echo "ERROR: Couldn't query aws stack" && exit -1))
endef

# To print the ECR URI:
get-ecr-uri:
	$(call get-ecr,AWS_ECR) && \
	echo "The SearchAPI ECR URI is:" && \
	echo "$${AWS_ECR}"

get-api-url: guard-TAG
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	export API_URL=$$(aws cloudformation describe-stacks \
		--stack-name "SearchAPI-$${TAG}" \
		--query "Stacks[?StackName=='SearchAPI-$${TAG}'][].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
		--output=text) && \
	echo "API URL for SearchAPI-$${TAG} is" && \
	echo "$${API_URL}"


###########################
## MAIN PIPELINE METHODS ##
###########################

#########################
### Deploy/Update Stacks:

## Update that registry with a container
docker-update-ecr: guard-TAG
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	$(call get-ecr,AWS_ECR) && \
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$${AWS_ECR}" && \
	docker build --pull --build-arg GIT_COMMIT_HASH="$${GITHUB_SHA:=Manual Makefile Deployment}" -t "$${AWS_ECR}:$${TAG}" . && \
	docker push "$${AWS_ECR}:$${TAG}"

## Deploy the API stack
#	In --stack-name, after TAG, will replace all non-alpha chars with '-'
update-api-stack-template: guard-TAG guard-MATURITY
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	aws cloudformation deploy \
		--stack-name "SearchAPI-$${TAG}" \
		--template-file cloudformation/SearchAPI-stack.yml \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			ContainerTag="$${TAG}" \
			Maturity="$${MATURITY}" \
			NumConcurrentExecutions="$${NumConcurrentExecutions:=1}" \
			AcmCertificateArn="$${AcmCertificateArn:=}"

## Update the Lambda, with the latest container
#    If the stack already exists, it won't grab the latest by itself
update-lambda-function: guard-TAG
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	$(call get-ecr,AWS_ECR) && \
	export FUNCTION=$$(aws cloudformation describe-stacks \
					--stack-name "SearchAPI-$${TAG}" \
					--query "Stacks[?StackName=='SearchAPI-$${TAG}'][].Outputs[?OutputKey=='LambdaFunction'].OutputValue" \
					--output=text) && \
	aws lambda update-function-code \
					--function-name "$${FUNCTION}" \
					--image-uri "$${AWS_ECR}:$${TAG}" \
					--no-cli-pager && \
	echo "Waiting for update to finish...." && \
	aws lambda wait function-updated \
					--function-name "$${FUNCTION}" && \
	echo "Updating lambda function DONE."

# Main deploy method.
# First list ANY of the guards that the functions it calls uses,
# to fail fast instead of failing when it finally gets to that job:
deploy-searchapi-stack: guard-TAG guard-MATURITY \
	docker-update-ecr update-api-stack-template update-lambda-function

##################
### Delete Stacks:

## Delete the SearchAPI stack
delete-searchapi-stack: guard-TAG
	# Delete it:
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	aws cloudformation delete-stack \
		--stack-name "SearchAPI-$${TAG}" && \
	echo "Waiting for stack delete to finish...." && \
	aws cloudformation wait stack-delete-complete \
		--stack-name "SearchAPI-$${TAG}" && \
	echo "Deleting stack DONE."

##############
### Test API:

test-api: guard-TAG
	export TAG="$${TAG//[^[:alnum:]]/-}" && \
	export API_URL=$$(aws cloudformation describe-stacks \
		--stack-name "SearchAPI-$${TAG}" \
		--query "Stacks[?StackName=='SearchAPI-$${TAG}'][].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
		--output=text) && \
	pytest -n "$${NUM_THREADS:-0}" $${PYTEST_ARGS} . --api "$${API_URL}"
