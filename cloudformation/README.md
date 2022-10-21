# SearchAPI, GitHub Actions, and CloudFormation

A quick guide on SearchAPI Automation.

## Deploying Stacks

**TLDR**: The `SearchAPI-stack.yml` cloudformation template is for a single API maturity (you need a second for a staging environment), and is automated though GitHub Actions. All the `single-deploy-*.yml`'s have to be deployed to the account for SearchAPI to work, but only need to be deployed ONCE by an admin.

### Deploying single-deploy Stacks

Deploy **in the order** listed here:

#### single-deploy-strings-macros.yml

- First deploy the Strings Macro template. It adds functions to CloudFormation that the other templates rely on:

```bash
aws cloudformation deploy \
    --stack-name CFN-StringMacros \
    --template-file cloudformation/single-deploy-string-macros.yml \
    --capabilities CAPABILITY_IAM
```

#### single-deploy-ecr.yml

- Then Setup ECR. Every stack uses the same ECR, and reference this stack directly, so you can't delete this stack if ANY SearchAPI stack exists. (There's an optional param when deploying SearchAPI, that lets you point to a different ECR stack if needed.).
  - You can't have ECR tied into the SearchAPI stack, because you lambda requires a container that exists in ECR to run, and there's no way to push it up between CloudFormation setting up ECR, and then Lambda if they're not separate.
- We attach a Lifecycle Policy to ECR here too, and this lets us remove older containers without giving the GitHub User permissions to delete images.

```bash
aws cloudformation deploy \
    --stack-name ECR-SearchAPI \
    --template-file cloudformation/single-deploy-ecr.yml
```

You can access the ECR URI by the command line, by running:

```bash
# IF you ever change this stack name, you'll have to override a default param (ImportValueEcrUri) when deploying SearchAPI to point to the different ECR stack.
aws cloudformation describe-stacks \
    --stack-name "ECR-SearchAPI" \
    --query "Stacks[?StackName=='ECR-SearchAPI'].Outputs[0][?OutputKey=='RegistryUri'].OutputValue" \
    --output=text
```

#### single-deploy-github-user.yml

This sets up a user with minimal permissions to create SearchAPI stacks from. We use this user in GitHub to automate stacks when branches are created.

```bash
aws cloudformation deploy \
    --template-file cloudformation/single-deploy-github-user.yml \
    --stack-name GitHub-SearchAPI-User \
    --capabilities CAPABILITY_NAMED_IAM
```

Of note, we can't / don't want to automate creating access and secret access keys! Once the user is created, you'll have to manually do this and add the secrets to a GitHub Environment. (Environments are nice for having the same GitHub workflow be usable on multiple aws accounts. You can add them to the repo directly if you only have one aws account).

### Deploying a SearchAPI Stack

If possible, just create a branch/fork in GitHub to have this done automatically. These notes are more for learning how it works to develop on the pipeline directly.

The generic deploy command looks like so:

```bash
export BRANCH="some_github_branch"
aws cloudformation deploy \
    --stack-name "SearchAPI-$${BRANCH//[^[:alnum:]]/-}" \
    --template-file cloudformation/SearchAPI-stack.yml \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        GitHubBranch=${BRANCH} \
        Maturity=devel
```

This will replace all non-alpha chars with "-", since stack names are a little restrictive. (Above would create a stack `SearchAPI-some-github-branch`, that points to `some_github_branch` on GitHub).

- The container must already exist in ECR for the deployment to work. (ECR URI: `${aws_registry}/searchapi:${GitHubBranch}` if the default ECR stack is used).

## GitHub Environments

Environments let you define secrets with the same keys, but different values. This is useful for deploying to multiple AWS accounts, with different credentials per Environment.

These Keys are currently expected in each Environment:

- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `MATURITY`: Environment variable set inside SearchAPI container

Repo secrets - same for every Environment but still expected to exist:

- `AWS_REGION`

## GitHub Actions

TODO: Figure out what info might be useful here once the actions are refactored more. (Maybe why codepipeline didn't work? What's in GitHub Actions vs AWS?).

- Useful link: <https://docs.github.com/en/actions/learn-github-actions/contexts#github-context>

## Notes for re-creating SearchAPI

For when we switch to using `asf_search` directly. Different notes to keep in mind from the pipeline point of view, that *might* make things easier?

- Keep testing requirements completely standalone and separate from the package code? Lets the test suite action be minimal. Maybe it's not worth, and just have it install everything?
- Have less SearchAPI maturities. Maybe even two? prod, and non-prod?. Right now they're being set though github environments, so having 5 seems awkward unless there's a better way. But a lot of that stuff can be something like environment variables with defaults/package constants (which CMR to use), or removed completely (health endpoint: "this_api". If they're there, they know the api. Not sure how to automatically populate that, so it's the main blocker I see for cutting down maturities).
  - Have cmr_url be a parameter-overrides option? What else?

