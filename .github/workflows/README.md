# GitHub Actions Notes

## Notes on this specific Repo

Some actions will only trigger from the **default** branch (like `delete`). Make sure the `devel` branch has your action changes, if you're updating the trigger lists!

We have github actions use the makefile directly, to not duplicate code. It also forces the makefile to never fall behind, and is a powerful tool for creating quick deployments locally easily.

### Reusable Actions

Any actions that begin with `reusable-*`, are designed to be called by multiple triggers. The "trigger action" will pass in the environment to use, so that the same reusable action can be called from **both** `prod` and `non-prod` environments.

### AWS "Trigger" Actions

Any action that begins with `aws-*`, is the "trigger action" for managing a stack in AWS. The filename should also contain what they do to that stack, and then which account they deploy to.

#### Creating a new API

To create an API, you can use a makefile for a one time deployment. OR add your branch to the actions that apply to where you want to deploy.

- For makefile deployments, see [this guide](../../cloudformation/README.md).
- If you want a new API in prod, but never delete it automatically with the branch, just add your branch to the different triggers in `aws-DeployStack-prod.yml`.
- If you wanted one to develop from instead, you might add your branch to ALL `aws-*Stack-*-nonprod.yml` actions.

## Learning GitHub Actions in General

With looking at what variables are available, what `on` triggers exist, etc, check out the main docs at <https://docs.github.com/en/actions/learn-github-actions/contexts#github-context>.

With specifically setting up reusable workflows, there's a good guide at <https://docs.github.com/en/actions/using-workflows/reusing-workflows>. The tools team keeps theirs at <https://github.com/ASFHyP3/actions>, so they'd be good examples to go off of, and you might just find the action you need.

If you're debugging, a trick that might help is to see what the different variables you have access to are [from here](https://docs.github.com/en/actions/learn-github-actions/contexts#example-printing-context-information-to-the-log):

```yml
steps:
    - name: Dump GitHub context
      id: github_context_step
      run: echo '${{ toJSON(github) }}'
    - name: Dump job context
      run: echo '${{ toJSON(job) }}'
    - name: Dump steps context
      run: echo '${{ toJSON(steps) }}'
    - name: Dump runner context
      run: echo '${{ toJSON(runner) }}'
    - name: Dump strategy context
      run: echo '${{ toJSON(strategy) }}'
    - name: Dump matrix context
      run: echo '${{ toJSON(matrix) }}'
```
