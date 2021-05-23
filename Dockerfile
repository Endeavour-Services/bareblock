FROM python:3.9
ADD requirements.txt requirements.txt  
ADD node/requirements.txt node_requirements.txt
ADD client/requirements.txt client_requirements.txt
ADD requirements_test.txt requirements_test.txt
RUN pip install -r requirements.txt -r requirements_test.txt -r node_requirements.txt  -r client_requirements.txt
ADD node/gpg_utils.py /app/node/gpg_utils.py
ARG NAME
RUN NAME=${NAME} python /app/node/gpg_utils.py
ADD . /app
WORKDIR /app
CMD cp /signatures/* /export/ && sleep 10 && NAME=${NAME} python -m node