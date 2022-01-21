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

## Run everything from the Lambda directoy:
WORKDIR "${LAMBDA_TASK_ROOT}"

## Copy required files:
COPY SearchAPI SearchAPI
COPY requirements.txt .
COPY setup.py .
COPY README.md .

## Install both requirements.txt, AND the SearchAPI package in this dir:
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}" .

## Cleanup to save space:
RUN rm -rf /var/cache/yum

EXPOSE 5000
## Nuke "default" entrypoint (Since it's for running in lambda). It gets set BACK to default, in template.yaml
ENTRYPOINT []
## The "exec" is for correct signal handling.
CMD ["/bin/bash", "-c", ". /opt/venv/bin/activate && exec python -m SearchAPI.application"]
