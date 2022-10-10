# Notes on Cloudformation

TODO:

- GitHub User, look at locking down apigateway more? Gateway doesn't support arn like other resources, so it's weird.
- If looking at Lambda in GUI, the Gateway doesn't show up as a trigger. See if adding a link has a down side or not.
- change the `cloudformation` dir to `automation`, so you can include github actions notes.
- Add throdelling for SearchAPI stack? There's an account limit already in place.
- Add cron to keep lambda warm. Look into what the clock should be.
changes for re-writing full SearchAPI itself.
- Attach a Lifecycle Policy to the ECR stack directly
- Will we need cloudfront in front of API Gateway, or use gateway directly?

SearchAPI Rewrite Notes:

- Keep testing requirements completely standalone and separate from the package code? Lets the test suite action be minimal. Maybe it's not worth, and just have it install everything?
- Have less SearchAPI maturities. Maybe even two? prod, and non-prod?. Right now they're being set though github environments, so having 5 seems awkward unless there's a better way. But a lot of that stuff can be something like environment variables with defaults/package constants (which CMR to use), or removed completely (health endpoint: "this_api". If they're there, they know the api. Not sure how to automatically populate that, so it's the main blocker I see for cutting down maturities).
  - Have cmr_url be a parameter-overrides option? What else?
  - If you need a "prod cmr_uat" API, create a third environment for that? Problem is you'd need a separate gh action for each environment. I hope there's a way to say "If branch name matches environment, run there. Else run in this non-prod environment".

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
