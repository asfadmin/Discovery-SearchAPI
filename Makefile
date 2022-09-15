SHELL := /bin/bash # Use bash syntax


update-macro-template:
	aws cloudformation deploy \
		--stack-name CFN-StringMacros \
		--template-file cloudformation/cf-string-macros.yml \
		--capabilities CAPABILITY_IAM

update-main-stack-template:
	aws cloudformation deploy \
		--stack-name ${STACK_NAME} \
		--template-file cloudformation/cf-stack.yml \
		--capabilities CAPABILITY_IAM

all: update-macro-template update-main-stack-template
