from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

import os
import json
from hashlib import sha256
import redis

from app import config
from app import exceptions as block_chain_errors


r = redis.Redis.from_url(url=os.environ['REDISCLOUD_URL'])


class Transaction(BaseModel):
    timestamp: str
    sender: str
    receiver: str
    amount: float


class Block(BaseModel):
    index: int
    timestamp: str
    hash: Optional[str]
    previous_hash: str
    transactions: List = Field(default_factory=list)
    nonce: int = 0

    def get_hash(self):
        block_content = json.dumps(self.dict(), sort_keys=True)
        return sha256(block_content.encode()).hexdigest()

    @classmethod
    def find_by_index(cls, index):
        data = eval(r.get(index).decode('utf-8'))
        return cls(**data)


class Blockchain(BaseModel):
    name: str
    difficulty: int = config.default_difficulty
    # chain: Optional[List] = Field(default_factory=list)
    # pending_transactions: List = Field(default_factory=list)

    @property
    def pending_transactions(self) -> List[Transaction]:
        stored_data = [b.decode('utf-8') for b in r.lrange('pending_transactions', 0, -1)]
        data = []
        for transaction_str in stored_data:
            transaction_dict = eval(transaction_str)
            data.append(Transaction(**transaction_dict))
        return data

    @property
    def chain(self) -> List[Block]:
        chain_data = list()
        if self.last_block != 0:
            for i in range(1, self.last_block_index):
                block = Block.find_by_index(i)
                chain_data.append(block)
        return chain_data

    @property
    def last_block_index(self) -> int:
        # return self.chain[-1]
        return eval(r.get('last_block').decode('utf-8'))

    @property
    def last_block(self) -> Block:
        return Block.find_by_index(self.last_block_index)

    @property
    def transactions(self) -> List[Transaction]:
        transactions = list()
        for block in self.chain:
            for trans_dict in block.transactions:
                transactions.append(Transaction(**trans_dict))
        return transactions

    def create_genesis_block(self):
        if len(self.chain) == 0:
            genesis_block = Block(
                index=0,
                timestamp=datetime.now().strftime(config.timestamp_fmt),
                previous_hash="0"
            )
            genesis_block.hash = genesis_block.get_hash()
            r.set('last_block', 0)
            r.set(0, genesis_block.json())
            # self.chain.append(genesis_block)
        else:
            raise block_chain_errors.blockchain_not_empty_error

    def add_block(self, new_block, proof) -> bool:
        # Check whether the previous hash of block is matched with the has of last block
        if new_block.previous_hash != self.last_block.hash:
            raise block_chain_errors.mismatch_hash_error

        # Validate whether the proof satisfy the difficulty criteria
        if not (proof.startswith('0' * self.difficulty) and proof == new_block.get_hash()):
            raise block_chain_errors.invalid_proof_error

        new_block.hash = proof
        # self.chain.append(new_block)
        r.set(new_block.index, new_block.json())
        return True

    def proof_of_work(self, new_block) -> str:
        """
        Proof of work process.
        Try to adjust the nonce value to satisfy the difficultly criteria
        """
        proof = new_block.get_hash()
        while not proof.startswith('0' * self.difficulty):
            new_block.nonce += 1
            proof = new_block.get_hash()
        return proof

    def add_new_transaction(self, transaction):
        # self.pending_transactions.append(transaction)
        r.rpush('pending_transactions', transaction.json())

    def mine(self) -> int:
        """
        Do the proof of work, return the index of new added block
        """
        if len(self.pending_transactions) == 0:
            raise block_chain_errors.no_pending_transaction_error

        last_block = self.last_block

        new_block = Block(
            index=last_block.index + 1,
            transactions=self.pending_transactions,
            timestamp=datetime.now().strftime(config.timestamp_fmt),
            previous_hash=last_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        # self.pending_transactions = []
        r.delete('pending_transactions')
        return new_block.index


