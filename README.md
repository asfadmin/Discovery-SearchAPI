# SearchAPI

Search API for talking with CMR.

## Development

### Install and enviornment for running the first time

1. Clone a local copy of this repo:

> ~$ git clone git@github.com:asfadmin/Discovery-SearchAPI.git

> ~$ cd Discovery-SearchAPI


2. Create a virtual environment:

> ~$ virtualenv --python=python3 ~/SearchAPI-env


3. Activate the virtual environmen, make sure the label appears:

> ~$ source ~/SearchAPI-env/bin/activate

> (SearchAPI-env) ~$


4. Use pip to install requirements:

> (SearchAPI-env) ~$ pip install -r requirements.txt

- At the time of this writing, in some situations you may encounter an SSL certificate error. If that happens, re-install pip using the following command and try step 4 again:

> curl https://bootstrap.pypa.io/get-pip.py | python

### 

1. If not already started, activate the enviornment:

```bash
~$ source ~/SearchAPI-env/bin/activate
```

2. Run the dev server

```bash
(ProxyAPI-env) ~$ python application.py
```

3. After making changes, pylint your code

```bash
(ProxyAPI-env) ~$ pylint --rcfile=pylintrc <changed files>
```

4. If you install new modules with pip, update requirements.txt:

```bash
(ProxyAPI-env) ~$ pip freeze > requirements.txt
```

# Testing
Testing is done using the [Discovery-PytestAutomation](https://github.com/asfadmin/Discovery-PytestAutomation) repo.

> git clone https://github.com/asfadmin/Discovery-PytestAutomation

> cd Discovery-PytestAutomation

> pytest {pytest flags here} . {PytestAutomation flags here}

   - See [here](https://github.com/asfadmin/Discovery-PytestAutomation) for filters/flags for PytestAutomation.
   - See [here]() for custom flags, unique to this project.

# Installing

## Windows Subsystem for Linux:

1) Update your package list

> sudo apt update

2) Install missing libraries from apt
```
sudo apt install python3-pip python3-testresources libgeos-dev
```

3) Install missing libraries from pip
```
pip3 install -r requirements.txt
```
# Production
To deploy to prod, merge changes to the prod branch.
