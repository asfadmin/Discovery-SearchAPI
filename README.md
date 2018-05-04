# api-proxy
Switching proxy API for CMR and legacy ASF API. The proxy converts queries to CMR queries where possible and translates the results to ASF API style results. If a query can't be translated, the proxy acts as a passthrough to the legacy ASF API.

# Development
To get started with a local instance for development:

1. Clone a local copy of this repo:
```
~$ git clone git@github.com:asfadmin/api-proxy.git
~$ cd api-proxy
```

2. Create a virtual environment:
```
~$ virtualenv ~/api-proxy-env
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

5. Run the dev server
```
(api-proxy-env) ~$ python application.py
```

# Testing
To deploy to test, merge changes to the test branch.

# Production
To deploy to prod, merge changes to the prod branch.
