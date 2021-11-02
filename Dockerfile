# From aws's repository:
FROM amazon/aws-lambda-python:3

## Install/update outside libraries:
RUN yum update -y
RUN yum install -y g++ gcc-c++
RUN yum -y clean all

# Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
# ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
# RUN chmod +x /usr/bin/aws-lambda-rie

### TODO: Poke at dropping to non-root here <---------------------------------------------------------------------- !!!!!!!!!!!!!!!!!!!!!!!!

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel Cython awslambdaric
RUN python3 -m pip install wheel Cython
    # wheel Cython => building (mainly scikit-learn)
    # awslambdaric => lambda runtime API: https://docs.aws.amazon.com/lambda/latest/dg/runtimes-images.html#runtimes-api-client
        # Maybe not needed? Since I'm building from amazon/aws-lambda-python container

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

## Copy required files:
ADD SearchAPI "${LAMBDA_TASK_ROOT}/SearchAPI"
ENV PYTHONPATH "${PYTHONPATH}:${LAMBDA_TASK_ROOT}/SearchAPI"

## Run everything from the SearchAPI directoy:
WORKDIR "${LAMBDA_TASK_ROOT}/SearchAPI"
CMD [ "application.handler" ]
