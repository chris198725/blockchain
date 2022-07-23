class BlockchainError(Exception):
    pass


blockchain_not_empty_error = BlockchainError('Unable to create genesis block as chain is not empty.')

# Add Block
mismatch_hash_error = BlockchainError('New hash does not match with the previous hash.')
invalid_proof_error = BlockchainError('Your proof is invalid.')

# Mining
no_pending_transaction_error = BlockchainError('There is no more pending transaction.')

