# SearchAPI

Docs on how to interface against our API instances [here](https://docs.asf.alaska.edu/api/basics/).

This is the backend, powering [ASF Search](https://search.asf.alaska.edu/#/).

## Public ECR images

- Prod (Recommended): `Coming Soon!`
- Test: `public.ecr.aws/asf-discovery/searchapi-test`
- Devel: `public.ecr.aws/asf-discovery/searchapi-devel`

If it complains you're not logged in, (assuming you have `~/.aws/credentials` setup), try running:

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

## Developing

### Python management with virtualenv

1) Install virtualenv, and update:

   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install virtualenv
   ```

2) Create and activate it:

   ```bash
   virtualenv --python=python3 ~/SearchAPI-env
   source ~/SearchAPI/bin/activate
   # Now you should see something like "(SearchAPI-env)".
   ```

3) Install all the packages:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Building API with Docker

This is more straight forward than the SAM method, and behaves more like Elastic Beanstalk. Use the SAM method if you need more of a "lambda" API.

### Building and Running the Container (Docker)

1) To build it locally, run:

   ```bash
   docker build -t searchapi .
   ```

2) Then to start it:

   ```bash
   docker run --net=host --rm searchapi
   ```

   You'll see output like `Listening at: http://127.0.0.1:8080`. Point the test suite there by using `--api <url>` to test the container locally.

## Building API with SAM

This isn't AS straight forward as docker, but is very close. SAM behaves the same as if you're hitting against AWS lambda. Use the docker method if you need a Elastic Beanstalk environment.

### Building and Running the Container (SAM)

1) To build it locally, run:

   ```bash
   sam build
   ```

2) Then to start it:

   ```bash
   sam local start-api --port 8080 --parameter-overrides Maturity=local
   ```

   You'll see output like `Listening at: http://127.0.0.1:8080`. Point the test suite there by using `--api <url>` to test the container locally.

## Run the Test Suite

Testing is done using the [Discovery-PytestAutomation](https://github.com/asfadmin/Discovery-PytestAutomation) plugin.

Once you have your environment installed, and want to test against one of the deployments above, run the following command:

```bash
pytest -n auto --df bugs --df prod_only . --api http://127.0.0.1:8080
```

- `-n auto`: Use however many threads your computer has. (can also run `-n 3` to set 3 threads).
  - If you want the clean output of how many tests per file are running, leave this flag out.
- `--df <some file>`: Short for `--dont-run-file`. If the file has this string in it's name, skip it.
  - More filters in the [pytest-automation docs](https://github.com/asfadmin/Discovery-PytestAutomation).
- `.`: Run from this directory (The path).
- `--api <url>`: The url to hit against. Also supports keys in SearchAPY/maturities.yml (like `local`, `test`, and `test-beanstalk`). This flag must always be after the path. (i.e. `.` above).

## Useful Tools and Links

- For checking headers for security, use <https://observatory.mozilla.org/>
  - This works with ALL websites, not just the API.

- For updating the whitelist on who can trigger codebuild builds, grab their ID from <https://api.github.com/users/SOME_USERNAME>.
  - You'll need the ID for whenever someone joins/leaves the team.
  - Each account has two codebuild projects that'll need updated.
