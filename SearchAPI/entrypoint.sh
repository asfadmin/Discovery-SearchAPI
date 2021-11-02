#!/bin/bash

# Modified from: https://docs.aws.amazon.com/lambda/latest/dg/images-test.html
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    exec /usr/bin/aws-lambda-rie python3 -m awslambdaric $@
else
    exec python3 -m awslambdaric $@
fi
