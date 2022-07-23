from fastapi import FastAPI
import json

from app.models import Blockchain, Transaction


app = FastAPI()

transaction_bc = Blockchain(name='Transaction Blockchain')
transaction_bc.create_genesis_block()


@app.get("/transactions")
async def get_transaction_history():
    data = []
    for block in transaction_bc.chain:
        for transaction in block.transactions:
            data.append(transaction)
    return json.dumps({
        "length": len(data),
        "transactions": data
    })


@app.post("/transaction")
async def add_transaction(transaction: Transaction):
    transaction_bc.add_new_transaction(transaction)
    return transaction


@app.post("/mining")
async def mining():
    transaction_bc.mine()
    return {
        "message": "Mining completed."
    }
