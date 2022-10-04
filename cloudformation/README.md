# Notes on Cloudformation

TODO:

- See if taking out the single-deploy's from the pipeline is a good idea, to limit github user permissions.
- Completely re-write this readme. Include:
  - How to re-deploy if account goes down.
    - Setup access keys for github user. Can't be automatic.
  - DO NOT automate the github user cloudformation note.
  - Why the ECR isn't apart of the stack.
  - Overall workflow, what's in Github Actions vs AWS
- Make sure GitHub cache will pull the latest container still. (And look closer at any params the action exposes)

## To Deploy

For now, run:

```bash
make -e BRANCH=<github_branch> all
```

## Working with the stack manually

- After making changes, to lint the stack:

```bash
cfn-lint cloudformation/cf-stack.yml
```

- To deploy the stack manually (example for test):
  - The only non-alpha char you should use for the StackName is '-'.

```bash
export AWS_DEFAULT_PROFILE="YOUR_PROFILE_HERE"
aws cloudformation deploy --template-file cloudformation/cf-stack.yml --capabilities CAPABILITY_IAM --stack-name SearchAPI-test --parameter-overrides LambdaDockerRegistry="public.ecr.aws/asf-discovery" GitHubBranch=test
```

- If that stack already exists, the lambda image of the stack won't grab the latest docker image. Force it to do so:

```bash
aws lambda update-function-code --function-name <function_name_here> --image-uri <same_as_LambdaDockerImage_above>
# That command doesn't block. If you want to wait for the function to finish updating to continue:
aws lambda wait function-updated --function-name <function_name_here>
```


