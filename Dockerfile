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

## copy/install requirements.txt first, to avoid re-running after every single edit to SearchAPI:
COPY requirements.txt .
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

## Copy required files:
COPY SearchAPI SearchAPI
COPY setup.py .
COPY README.md .

## Install the SearchAPI package in this dir:
RUN . /opt/venv/bin/activate && python3 -m pip install --no-cache-dir --target "${LAMBDA_TASK_ROOT}" .

## Cleanup to save space:
RUN rm -rf /var/cache/yum

## Host to open queries too. (localhost=127.0.0.1, outside_world=0.0.0.0)
ENV OPEN_TO_IP="127.0.0.1"
EXPOSE 80
# ## Nuke "default" entrypoint (Since it's for running in lambda). It gets set BACK to default, in template.yaml
ENTRYPOINT ["/bin/bash"]
# ## The "exec" is for correct signal handling.
CMD ["-c", ". /opt/venv/bin/activate && exec python3 -m gunicorn --bind ${OPEN_TO_IP}:80 --workers 2 --threads $(grep -c ^processor /proc/cpuinfo) SearchAPI.application:application"]
