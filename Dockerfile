# From aws's repository:
FROM public.ecr.aws/lambda/python:3.9

## Install/update outside libraries:
RUN yum update -y && \
    yum install -y g++ gcc-c++ && \
    yum -y clean all

RUN python3 -m venv /opt/venv

RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir wheel Cython
    # wheel Cython => building (mainly scikit-learn)

## Eerything needs to be in the Lambda directoy:
RUN mkdir "${LAMBDA_TASK_ROOT}/Discovery-SearchAPI"
WORKDIR "${LAMBDA_TASK_ROOT}/Discovery-SearchAPI"

## copy/install requirements.txt first, to avoid re-running after every single edit to SearchAPI:
COPY requirements.txt .
RUN mkdir "${LAMBDA_TASK_ROOT}/python-packages"
ENV PYTHONPATH "${PYTHONPATH}:${LAMBDA_TASK_ROOT}/python-packages"
RUN python3 -m pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}/python-packages"

## Copy required files (Already inside Discovery-SearchAPI dir):
COPY SearchAPI SearchAPI
COPY setup.py .
COPY README.md .

## Install the SearchAPI package in this dir:
RUN python3 -m pip install --no-cache-dir --target "${LAMBDA_TASK_ROOT}/python-packages" .

## Cleanup to save space:
RUN rm -rf /var/cache/yum

## Host to open queries too. (localhost=127.0.0.1, outside_world=0.0.0.0)
ENV OPEN_TO_IP="127.0.0.1"
EXPOSE 8080
# ## Nuke "default" entrypoint (Since it's for running in lambda). It gets set BACK to default, in template.yaml
ENTRYPOINT ["/bin/bash", "-l", "-c"]
CMD ["python3 -m gunicorn --bind ${OPEN_TO_IP}:8080 --workers 2 --threads $(grep -c ^processor /proc/cpuinfo) SearchAPI.application:application"]
