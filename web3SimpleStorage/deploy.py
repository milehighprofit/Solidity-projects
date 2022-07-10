from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    install_solc("0.8.0")



compiled_sol = compile_standard({

    "language": "Solidity",
    "sources":{"SimpleStorage.sol": {"content": simple_storage_file}},
    "settings": {
        "outputSelection": {
            "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    },
}, solc_version="0.8.0"
)


with open("./CompiledCode.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

w3 = Web3(Web3.HTTPProvider("https://eth-rinkeby.alchemyapi.io/v2/QjRzAsRPphrfrHfUarGY64jpNVoN_9oA"))
chain_id = 4
my_address = "0x02838296906D53eEe4e6BF986D1ec062d3eC743f"
private_key = os.getenv("PRIVATE_KEY")


SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price,"chainId": chain_id, "from": my_address, "nonce": nonce})

signedtxn= w3.eth.account.sign_transaction(transaction, private_key=private_key)

txnhash = w3.eth.send_raw_transaction(signedtxn.rawTransaction)

txreceipt = w3.eth.wait_for_transaction_receipt(txnhash)

simple_storage = w3.eth.contract(address=txreceipt.contractAddress, abi=abi)

#initial value of fav number
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

signedStoreTxn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)

transactionHash = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)

transactionreceipt = w3.eth.wait_for_transaction_receipt(transactionHash)
print(simple_storage.functions.retrieve().call())