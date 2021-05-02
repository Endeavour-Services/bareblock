- [x] create n identities
- [ ] permanent store ???
- [x] server based model


- [x] message schema
- [x] check message shcema valid
  - [ ] test message schema
- [x] check client name (pgp takes care of it)

- [x] 100 messages, pluck and store in seperate store
  - [ ] check block created after 100 messages
- [x] hash of messages
  - [ ] check hash of message
- [x] sign of hash
  - [ ] check sign of message



- [x] number of blocks completed
  - [ ] test number of blocks completed
  - [ ] if no blocks, should respond zero
  - [ ] with more messages, block should increment
- [x] get block from index
  - [ ] test block from index
  - [ ] if no block should respond in so
- [x] get latest of block
  - [ ] test latest block
  - [ ] if no latest block should respond
- [x] from hash, pick previous block
  - [ ] test previous block
  - [ ] if no previous block, should respond in so
- [x] implement encryption, so only node can read messages