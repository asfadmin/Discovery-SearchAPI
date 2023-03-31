# SearchAPI v3 Minimal Example

Quick setup:

```bash
# Setup a NEW virtual-env:
virtual-env --python=python3 ~/SearchAPIv3-env
source ~/SearchAPIv3-env/bin/activate
# Probably a more minimal package set exists, but for now grab everything:
python3 -m pip install fastapi[all] uvicorn mangum
# Build the container and push it to AWS:
cd SearchAPI-v3
make build
# Create the stack:
make deploy
```

Lambda:
    You can now test the lambda by going to the lambda function, test tab, then selecting "cloudfront-modify-querystring" for the template. The basic function returns whatever is in the url for a response, the default test should return `"body": "{\"result\":\"test\"}"` somewhere inside the json block. (since it hit `/test?otherparams=foo`).

Beanstalk:
    TODO
