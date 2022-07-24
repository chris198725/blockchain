from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

import json
from hashlib import sha256

from app import config
from app import exceptions as block_chain_errors


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


class Blockchain(BaseModel):
    name: str
    difficulty: int = config.default_difficulty
    chain: Optional[List] = Field(default_factory=list)
    pending_transactions: List = Field(default_factory=list)

    def create_genesis_block(self):
        if len(self.chain) == 0:
            genesis_block = Block(
                index=0,
                timestamp=datetime.now().strftime(config.timestamp_fmt),
                previous_hash="0"
            )
            genesis_block.hash = genesis_block.get_hash()
            self.chain.append(genesis_block)
        else:
            raise block_chain_errors.blockchain_not_empty_error

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, new_block, proof) -> bool:
        # Check whether the previous hash of block is matched with the has of last block
        if new_block.previous_hash != self.last_block.hash:
            raise block_chain_errors.mismatch_hash_error

        # Validate whether the proof satisfy the difficulty criteria
        if not (proof.startswith('0' * self.difficulty) and proof == new_block.get_hash()):
            raise block_chain_errors.invalid_proof_error

        new_block.hash = proof
        self.chain.append(new_block)
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
        self.pending_transactions.append(transaction)

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

        self.pending_transactions = []
        return new_block.index


class Transaction(BaseModel):
    timestamp: str
    sender: str
    receiver: str
    amount: float


