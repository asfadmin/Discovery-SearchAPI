# SearchAPI, GitHub Actions, and CloudFormation

A quick guide on SearchAPI Automation.

## Deploying Stacks

**TLDR**: The `SearchAPI-stack.yml` cloudformation template is for a single API maturity (you'd need a second for a staging environment), and is automated though the [Makefile](../Makefile). All the `single-deploy-*.yml`'s have to be deployed to the account FIRST for SearchAPI to work, but only need to be deployed ONCE by an admin.

### Deploying single-deploy Stacks

Deploy **in the order** listed here:

Note: anywhere in make commands you see `-e KEY=Value`, you can also do `export KEY=VALUE` separately to not have to add it every time. This might be useful when developing on stacks.

#### single-deploy-strings-macros.yml

- First deploy the Strings Macro template. It adds functions to CloudFormation that the other templates rely on:

```bash
make -e AWS_PROFILE=<admin_profile_here> single-deploy-macro-template
```

#### single-deploy-ecr.yml

- Then Setup ECR. Every stack uses the same ECR, and reference this stack directly, so you can't delete this stack if ANY SearchAPI stack exists. (There's an optional param when deploying SearchAPI, that lets you point to a different ECR stack if needed.).
  - You can't have ECR tied into the SearchAPI stack, because you lambda requires a container that exists in ECR to run, and there's no way to push it up between CloudFormation setting up ECR, and then Lambda if they're not separate.
- We attach a Lifecycle Policy to ECR here too, and this lets us remove older containers without giving the GitHub User permissions to delete images.

```bash
make -e AWS_PROFILE=<admin_profile_here> single-deploy-searchapi-ecr
```

You can access the ECR URI by the command line, by running:

```bash
make get-ecr-uri
```

There's no way to automatically delete **tagged** images though lifecycle policies (unless you already know their name). Someone will have to jump in and delete old tags once in a while. Untagged images are deleted automatically if there's too many, and MOST of the images will be untagged. This won't have to happen that often at all.

#### single-deploy-github-user.yml

This sets up a user with minimal permissions to create SearchAPI stacks from. We use this user in GitHub to automate stacks when branches are created.

```bash
make -e AWS_PROFILE=<admin_profile_here> single-deploy-github-user
```

Of note, we can't / don't want to automate creating access and secret access keys! Once the user is created, you'll have to manually do this and add the secrets to a GitHub Environment. (Environments are nice for having the same GitHub workflow be usable on multiple aws accounts. You can add them to the repo directly if you only have one aws account).

### Deploying a SearchAPI Stack

The generic deploy command looks like:

```bash
make -e MATURITY=<api_maturity> -e TAG=<deploy_tag> deploy-searchapi-stack
```

So for example:

```bash
make -e MATURITY=devel -e TAG=test
```

Will create an API to develop against, with the stack name `SearchAPI-test`. The "SearchAPI-" part is appended automatically! This will also create a docker tag `test` inside ECR that the stack uses.

The `TAG` value will replace all non-alpha chars with "-", since stack names are a little restrictive. (If a branch named `some_github_branch` triggered the pipeline, that would become the `TAG`, and it would create a stack named `SearchAPI-some-github-branch`).

You can also get the URL of a stack with:

```bash
make -e TAG=<deploy_tag> get-api-url
```

### Deleting a SearchAPI Stack

The generic delete command looks like:

```bash
make -e TAG=<same_tag_as_before> delete-searchapi-stack
```

## Developing on the SearchAPI Stack itself

- After making changes, lint the stack:

  ```bash
  cfn-lint cloudformation/cf-stack.yml
  ```

  This'll return back feedback FAR faster than trying to deploy the stack.

## GitHub Environments

Environments let you define secrets with the same keys, but different values. This is useful for deploying to multiple AWS accounts, with different credentials per Environment.

These Keys are currently expected in each Environment:

- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `MATURITY`: Environment variable set inside SearchAPI container

Repo secrets - same for every Environment but still expected to exist:

- `AWS_REGION`

## GitHub Actions

Guide for the Actions themselves can be found [here](./../.github/workflows/README.md).

## Notes for re-creating SearchAPI

For when we switch to using `asf_search` directly. Different notes to keep in mind from the pipeline point of view, that *might* make things easier?

- Keep testing requirements completely standalone and separate from the package code? Lets the test suite action be minimal. Maybe it's not worth, and just have it install everything?
- Have less SearchAPI maturities. Maybe even two? prod, and non-prod?. Right now they're being set though github environments, so having 5 seems awkward unless there's a better way. But a lot of that stuff can be something like environment variables with defaults/package constants (which CMR to use), or removed completely (health endpoint: "this_api". If they're there, they know the api. Not sure how to automatically populate that, so it's the main blocker I see for cutting down maturities).
  - Have cmr_url be a parameter-overrides option? What else?
  - If you need a "prod cmr_uat" API, create a third environment for that? Problem is you'd need a separate gh action for each environment. I hope there's a way to say "If branch name matches environment, run there. Else run in this non-prod environment".
