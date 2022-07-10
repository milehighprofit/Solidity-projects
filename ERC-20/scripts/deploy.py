from scripts.helpfulscripts import get_account
from brownie import MyToken, config, network

def deploy_token():
    account = get_account()
    mytoken = MyToken.deploy(10000, {"from": account},
    publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print
    return mytoken





def main():
    deploy_token()
