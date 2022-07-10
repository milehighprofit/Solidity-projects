from brownie import accounts, config, SimpleStorage, network

def deploy_simple_storage():
    account = get_account()

    simple_storage = SimpleStorage.deploy({'from': account})
    #account = accounts.load("Burnwallet")
    #print(account)
    #account = accounts.add(config["wallets"]["from_key"])
    #print(account)
    transaction = simple_storage.store(15, {'from': account})
    transaction.wait(1)
    store_value = simple_storage.retrieve()
    print(transaction)
    print(store_value)

def get_account():
    if network.show_active == "development":
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["from_key"])

def main():
    deploy_simple_storage()
