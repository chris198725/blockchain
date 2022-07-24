from fastapi import FastAPI, HTTPException, status
import json

from app.models import Blockchain, Transaction


app = FastAPI()

transaction_bc = Blockchain(name='Transaction Blockchain')
transaction_bc.create_genesis_block()


@app.get("/blocks")
async def get_blocks():
    try:
        data = []
        for block in transaction_bc.chain:
            data.append(block.dict())
        return json.dumps({
            "length": len(data),
            "blocks": data
        })
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.get("/transactions")
async def get_transaction_history():
    try:
        data = []
        for block in transaction_bc.chain:
            for transaction in block.transactions:
                data.append(transaction.dict())
        return json.dumps({
            "length": len(data),
            "transactions": data
        })
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.get("/pending-transactions")
async def get_pending_transactions():
    try:
        data = []
        for transaction in transaction_bc.pending_transactions:
            data.append(transaction.dict())
        return json.dumps({
            "length": len(transaction_bc.pending_transactions),
            "transactions": data
        })
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
