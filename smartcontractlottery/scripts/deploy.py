from scripts.helpfulscripts import get_account, get_contracts, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contracts("eth_usd_price_feed").address,
        get_contracts("vrf_coordinator").address,
        get_contracts("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery
    

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from":account})
    starting_tx.wait(1)

    print("the lottery is started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1] 
    value = lottery.getEntranceFee() + 10000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("you entered lottery lad")

def end_lottery():
    account = get_account
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait()
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.RecentWinner()}is the new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()