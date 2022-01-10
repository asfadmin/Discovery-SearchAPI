# From aws's repository:
FROM public.ecr.aws/lambda/python:3.9

## Install/update outside libraries:
RUN yum update -y && \
    yum install -y g++ gcc-c++ && \
    yum -y clean all

RUN python3 -m venv /opt/venv

RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir --upgrade pip
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir wheel Cython
    # wheel Cython => building (mainly scikit-learn)

COPY requirements.txt .
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

## Copy required files:
ADD SearchAPI "${LAMBDA_TASK_ROOT}/SearchAPI"
ENV PYTHONPATH "${PYTHONPATH}:${LAMBDA_TASK_ROOT}/SearchAPI"

## Cleanup to save space:
RUN rm -rf /var/cache/yum

## Run everything from the SearchAPI directoy:
WORKDIR "${LAMBDA_TASK_ROOT}/SearchAPI"
CMD [ "application.application" ]
