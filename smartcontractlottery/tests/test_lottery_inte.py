from brownie import Lottery, accounts, config, network, exceptions
from scripts.helpfulscripts import LOCAL_BLOCKCHAIN_ENVIROMENTS, get_account, fund_with_link, get_contracts
import pytest
from scripts.deploy import deploy_lottery
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()  

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value":lottery.getEntranceFee(), "gas": 0xF4240, "gasPrice": 0x4A817C800})
    lottery.enter({"from": account, "value":lottery.getEntranceFee(), "gas": 0xF4240, "gasPrice": 0x4A817C800})
    fund_with_link(lottery)
    lottery.endLottery({"from":account})
    time.sleep(60)

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

