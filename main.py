from fastapi import FastAPI, HTTPException, status
import json

from app.models import Blockchain, Block, Transaction


app = FastAPI(name='Blockchain')

transaction_bc = Blockchain(name='Blockchain')
transaction_bc.init()


@app.get("/block/{block_index}")
async def get_block(block_index):
    block = Block.find_by_index(block_index)
    return block.dict()


@app.get("/blocks")
async def get_blocks():
    try:
        data = [block.dict() for block in transaction_bc.chain]
        return {
            "length": len(data),
            "blocks": data
        }
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.get("/transactions")
async def get_transaction_history():
    try:
        data = []
        for block in transaction_bc.chain:
            for transaction in block.transactions:
                data.append(transaction)
        return {
            "length": len(data),
            "transactions": data
        }
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.get("/pending-transactions")
async def get_pending_transactions():
    try:
        data = [transaction.dict() for transaction in transaction_bc.pending_transactions]
        return {
            "length": len(data),
            "transactions": data
        }
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.post("/transaction", response_model=Transaction)
async def add_transaction(transaction: Transaction):
    try:
        transaction_bc.add_new_transaction(transaction)
        return transaction
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))


@app.post("/mining")
async def mining():
    try:
        transaction_bc.mine()
        return {
            "message": "Mining completed."
        }
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
