from brownie import Lottery, accounts, config, network, exceptions
from requests import request
from web3 import Web3
from scripts.deploy import deploy_lottery
from scripts.helpfulscripts import LOCAL_BLOCKCHAIN_ENVIROMENTS, get_account, fund_with_link, get_contracts
import pytest

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    expected = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert expected == entrance_fee

def test_cant_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip() 
    
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value":lottery.getEntranceFee()})
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()  
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value":lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from":account})

    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()  
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value":lottery.getEntranceFee()}) 
    lottery.enter({"from": get_account(index=1), "value":lottery.getEntranceFee()}) 
    lottery.enter({"from": get_account(index=2), "value":lottery.getEntranceFee()}) 
    fund_with_link(lottery)
    txn = lottery.endLottery({"from":account})
    request_id = txn.events["requestedRandomness"]["requestId"]
    STATIC_RNG=777
    get_contracts("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})
    starting_balance = account.balance()
    lottery_balance = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance + lottery_balance


