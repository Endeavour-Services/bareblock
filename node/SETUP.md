## Docker

Install docker by following steps in [here](https://docs.docker.com/engine/install/)

`docker-compose up`

## Running tests

`docker-compose build`



## Non docker

current project uses `python3`

# setup 
`python -m pip install -r requirements.txt -r requirements_test.txt -r client/requirements.txt -r node/requirements.txt`


### running node
`python -m node`
### running client
`python -m client <client_name>`

for example
`python -m client client_1`
`python -m client client_2`

## Running tests

python -m unittest