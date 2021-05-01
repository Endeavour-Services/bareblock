
## Overview

- There are N clients with their own identities. The identity consists of {public, private} key-pair. N can be 10 or some decent number.

- There is a node (a server) that receives signed messages from the clients. The clients can use any protocol, such as TCP, HTTP, etc. to talk to the node. The node also has its own identity.

- The node will persist the messages received from the clients, so some form permanent data store is used. The implementation can use simple file-based storage, a key-value store, or an RDBMS. Keep it simple. 

- The interaction between clients and the node can be implemented in the client/server or peer-to-peer (p2p) model.

- The clients and node can be on the same physical machine. 


## Requirements

- Generate identities for N clients.

- Define a message of your choice. The message can be modeled in JSON or any format of your choice. The message schema is known to both the clients and the node. 

- Each client generates a message, signs it, and sends the signed message to the node. Each client is configured to generate and send a message every second, for 1 minute.

- The node validates the message received as follows:
  1. The message schema is valid.
  2. The message is signed.
  3. The signature is valid and the message indeed came from the client who sent it.

- If the validation succeeds, the node persists the message in the order the message is received.

- When the number of messages received reaches 100, the node processes the messages as follows.
  1. Plucks the 100 messages from its queue.
  2. Creates a hash of those messages.
  3. Signs the hash.
  4. Persists the signed hash, hash, and the 100 messages in a separate list. The order of the entry (block) in the list is the order in which the group of 100 messages arrived at the node. To keep the test simple, there is no blockchain created, but a simple list of blocks.

- The node exposes the following APIs, which can be called by the clients. Depending on the implementation, this can be just methods to call on the node, HTTP endpoints, etc. So, define the API format as required.
  1. Get the number of completed blocks.
  2. Get the block identified by index in the list.

Please identify the test cases, describe them, and demonstrate that the implementation passes the test cases.

A subset of the above functionality can be implemented, if the effort goes beyond a typical weekend’s worth of work. Please spell out what is excluded when submitting the work.


------

Bonus points
The following features earn extra credits. One or more of the following can be implemented.

- When the node creates blocks, create a Merkle tree of 100 messages. This produces Merkle root hash. Sign this hash and persist it.

- Create a blockchain instead of the simple list of blocks. Each block contains the hash of the previous block, so you can traverse the chain from the latest to the oldest block.

- With blockchain implemented, provide an API to get the latest (head) block.

- With blockchain implemented and given a block hash, provide an API to retrieve the previous block.
Implement encryption so the messages sent by the clients can only be decrypted by the node. The clients encrypt the messages using node’s public key, so only the node can decrypt the message using its private key.
------