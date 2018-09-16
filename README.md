# Proxy-API
Proxy API for CMR. The proxy converts ASF API style queries to CMR queries and translates the results to back ASF API style results. For complex API queries that CMR can not directly support, multiple sub-queries are performed, and the results combined.

# Development
To get started with a local instance for development:

1. Clone a local copy of this repo:
```
~$ git clone git@github.com:asfadmin/api-proxy.git
~$ cd api-proxy
```

2. Create a virtual environment:
```
~$ virtualenv --python=python3 ~/api-proxy-env
```

3. Activate the virtual environment:
```
~$ source ~/api-proxy-env/bin/activate
(api-proxy-env) ~$
```

4. Use pip to install requirements:
```
(api-proxy-env) ~$ pip install -r requirements.txt
```

  - At the time of this writing, in some situations you may encounter an SSL certificate error. If that happens, re-install pip using the following command and try step 4 again:
  ```
  curl https://bootstrap.pypa.io/get-pip.py | python
  ```

5. Run the dev server
```
(api-proxy-env) ~$ python application.py
```

6. After making changes, pylint your code:
```
(api-proxy-env) ~$ pylint --rcfile=pylintrc <changed files>
```

7. If you install new modules with pip, update requirements.txt:
```
(api-proxy-env) ~$ pip freeze > requirements.txt
```

# Testing
To deploy to test, merge changes to the test branch.

# Production
To deploy to prod, merge changes to the prod branch.
