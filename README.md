# ProxyAPI
Proxy API for CMR. The proxy converts ASF API style queries to CMR queries and translates the results to back ASF API style results. For complex API queries that CMR can not directly support, multiple sub-queries are performed, and the results combined.

# Development
To get started with a local instance for development:

1. Clone a local copy of this repo:
```
~$ git clone git@github.com:asfadmin/ProxyAPI.git
~$ cd ProxyAPI
```

2. Create a virtual environment:
```
~$ virtualenv --python=python3 ~/ProxyAPI-env
```

3. Activate the virtual environment:
```
~$ source ~/ProxyAPI-env/bin/activate
(ProxyAPI-env) ~$
```

4. Use pip to install requirements:
```
(ProxyAPI-env) ~$ pip install -r requirements.txt
```
>   If you hit the error **"OSError: Could not find library geos_c or load any of its variants ['libgeos_c.so.1', 'libgeos_c.so']"**, then run:
>
>   ```
>   sudo apt install libgeos-dev
>   ```

```
(ProxyAPI-env) ~$ pip install git+ssh://git@github.com/asfadmin/Discovery-Utils.git@prod --upgrade
```

  - At the time of this writing, in some situations you may encounter an SSL certificate error. If that happens, re-install pip using the following command and try step 4 again:
  ```
  curl https://bootstrap.pypa.io/get-pip.py | python
  ```

5. Run the dev server
```
(ProxyAPI-env) ~$ python application.py
```

6. After making changes, pylint your code:
```
(ProxyAPI-env) ~$ pylint --rcfile=pylintrc <changed files>
```

7. If you install new modules with pip, update requirements.txt:
```
(ProxyAPI-env) ~$ pip freeze > requirements.txt
```

# Testing
Testing is done using the [Discovery-PytestAutomation](https://github.com/asfadmin/Discovery-PytestAutomation) repo.

1) Git clone https://github.com/asfadmin/Discovery-PytestAutomation
2) cd Discovery-PytestAutomation
3) pytest . (See repo for filters/flags for running suite).

# Production
To deploy to prod, merge changes to the prod branch.
