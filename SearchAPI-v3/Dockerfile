FROM public.ecr.aws/lambda/python:3.8

# Work from this location:
WORKDIR ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target . -U --no-cache-dir

# Copy function code
COPY main.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
