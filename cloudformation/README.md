# Notes on Cloudformation

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

## Approve the GitHub Connection for a New Stack

This has to be done in the AWS console, and you need to be logged into GitHub at the same time.

1) After deploying the new stack, find the new CodePipeline in AWS.

2) On the very left, you'll see a bunch of collapsed options (Source, Artifacts, Build, Deploy, ...), Open the last one (Settings), and click "Connections".

3) You should see your new connection on the table, with status as "Pending". Walk though the steps in the GUI to connect it. (I'm not sure if you have to be a GitHub Owner or not. Let us know if it fails).
