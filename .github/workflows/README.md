# GitHub Actions Notes

## Notes on this specific Repo

### Reusable Actions

Any actions that begin with `reusable-*`, are designed to be called by multiple triggers. The trigger action will pass in the environment to use, so that the reusable actions can be called from `both` prod and `non-prod` environments.

### AWS Actions

Any action that begins with `aws-*`, is for managing a stack in AWS. The filename should also contain what they do tto that stack, and then which account they deploy to.

#### Creating a new API

To create an API, add your branch to the actions that apply to where you want to deploy.

- If you want a new API in prod, but never delete it automatically with the branch, just add your branch to the different triggers in `aws-DeployStack-prod.yml`.
- If you wanted one to develop from instead, you might add your branch to ALL `aws-*Stack-*-nonprod.yml` actions.

## Learning GitHub Actions in General

With looking at what variables are available, what `on` triggers exist, etc, check out the main docs at <https://docs.github.com/en/actions/learn-github-actions/contexts#github-context>.

With specifically setting up reusable workflows, there's a good guide at <https://docs.github.com/en/actions/using-workflows/reusing-workflows>. The tools team keeps theirs at <https://github.com/ASFHyP3/actions>, so they'd be good examples to go off of, and you might just find the action you need.
