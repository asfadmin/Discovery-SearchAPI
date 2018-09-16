# Proxy-API
Proxy API for CMR. The proxy converts ASF API style queries to CMR queries and translates the results to back ASF API style results. For complex API queries that CMR can not directly support, multiple sub-queries are performed, and the results combined.

# Development
To get started with a local instance for development:

1. Clone a local copy of this repo:
```
~$ git clone git@github.com:asfadmin/Proxy-API.git
~$ cd Proxy-API
```

2. Create a virtual environment:
```
~$ virtualenv --python=python3 ~/proxy-api-env
```

3. Activate the virtual environment:
```
~$ source ~/proxy-api-env/bin/activate
(proxy-api-env) ~$
```

4. Use pip to install requirements:
```
(proxy-api-env) ~$ pip install -r requirements.txt
```

  - At the time of this writing, in some situations you may encounter an SSL certificate error. If that happens, re-install pip using the following command and try step 4 again:
  ```
  curl https://bootstrap.pypa.io/get-pip.py | python
  ```

5. Run the dev server
```
(proxy-api-env) ~$ python application.py
```

6. After making changes, pylint your code:
```
(proxy-api-env) ~$ pylint --rcfile=pylintrc <changed files>
```

7. If you install new modules with pip, update requirements.txt:
```
(proxy-api-env) ~$ pip freeze > requirements.txt
```

# Testing
To deploy to test, merge changes to the test branch.

# Production
To deploy to prod, merge changes to the prod branch.
