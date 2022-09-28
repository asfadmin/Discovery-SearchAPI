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
		--template-file cloudformation/cf-string-macros.yml \
		--capabilities CAPABILITY_IAM

## Finally deploy the main stack
#	In --stack-name, after BRANCH, will replace all non-alpha chars with '-'
update-main-stack-template: guard-BRANCH
	aws cloudformation deploy \
		--stack-name "SearchAPI-$${BRANCH//[^[:alnum:]]/-}" \
		--template-file cloudformation/cf-stack.yml \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides GitHubBranch=${BRANCH}

all: update-macro-template update-main-stack-template
