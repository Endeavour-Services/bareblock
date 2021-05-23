- [x] create n identities
- [ ] permanent store --> Using in-memory for now, It can be added.
- [x] server based model


- [x] message schema
- [x] check message shcema valid
  - [x] test message schema
- [x] check client name (pgp takes care of it)

- [x] 100 messages, pluck and store in seperate store --> Currently set to 5, it can be changed.
  - [x] check block created after 100 messages
- [x] hash of messages
  - [x] check hash of message
- [x] sign of hash
  - [x] check sign of message

- [ ] Markle Tree implementation



- [x] number of blocks completed
  - [x] test number of blocks completed
  - [x] if no blocks, should respond as zero
  - [ ] with more messages, block should increment
- [x] get block from index
  - [x] test block from index
  - [x] if no block should show message
- [x] get latest of block
  - [x] test latest block
  - [x] if no latest block should show message
- [x] from hash, pick previous block
  - [x] test previous block
  - [x] if no previous block, should  show message
- [x] implement encryption, so only node can read messages