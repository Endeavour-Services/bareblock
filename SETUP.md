# Docker

Install docker by following steps in [here](https://docs.docker.com/engine/install/)

## Build docker
`docker-compose build`

## Running tests
`docker-compose up`

----

# Non Docker Setup 
Current project uses `python3`

`python3 -m pip install -r requirements.txt -r requirements_test.txt -r client/requirements.txt -r node/requirements.txt`

### Create GPG Home for clients
`mkdir clients_root`

### Running node
`python3 -m node`

### Running client
`python3 -m client <client_name>`

for example:

`python3 -m client client_1`

`python3 -m client client_2`

----
## APIs

*   To register a client
```

curl -X POST \
-H 'Content-Length: 996' \
-H 'content-type: application/json' \
-d '{
    "pgp": "\n-----BEGIN PGP PUBLIC KEY BLOCK-----\nmQENBGCNfg4BCAC887+7jSE/..........+j07t7zA1y9P3SFTPmtu52OM860w==\n=MxLx\n-----END PGP PUBLIC KEY BLOCK-----\n"
}' \
http://localhost:5000/register

```

*   To send a amessage

```
curl -X POST \
-H 'Content-Length: 578' \
-H 'content-type: application/json' \
-d '{
    "message": "\n-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA512\n\ntest\n-----BEGIN PGP SIGNATURE-----\n\niQEzBAEBCgAdFiEE8HTY7/b0ss+ssQBknJZQE9HzjaoFAmCN/wgACgkQnJZQE9Hz\njaponwf9FUKeKxXEzEHiHD8eIXe92G7qTo9EfsTGFDLGKM0Bi......pSfsjlUzcP10ctM5pzmJN9UFGKGpn4xpiZHFsOy39cSEYgGnPodJA16/GMw+sU\niJ5KVXQCtky5gu/sI5ye/gHajSFerA==\n=eVyq\n-----END PGP SIGNATURE-----"
}' \
http://localhost:5000/message
```


*   To get the total number of blocks information
```
curl -X GET \
http://localhost:5000/block/count
```

*   To get the list of blocks information
```
curl -X GET \
http://localhost:5000/block/list
```

*   To get the latest block information
```
curl -X GET \
http://localhost:5000/block/latest
```

*   To get the information using a block index
```
curl -X GET \
http://localhost:5000/block/index/1
```

*   To get a block information using it's hash
```
curl -X GET \
http://localhost:5000/block/47cecb46....
```

*   To get the previous block information using a block hash
```
curl -X GET \
http://localhost:5000/block/previous/47cecb.....
```
----

## To run test manually
`python3 -m unittest`