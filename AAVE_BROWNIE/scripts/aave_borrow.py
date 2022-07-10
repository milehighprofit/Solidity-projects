from brownie import accounts
from scripts.helpfulscripts import get_account
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3


AMOUNT = Web3.toWei(0.1, "ether")

def get_lending_pool():
    address_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addresses_provider"])
    lending_pool_address = address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

def approve_erc20(amount, spender, erc_20_address, account):
    print("approving token")
    erc = interface.IERC20(erc_20_address)
    tx = erc.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"you have {available_borrow_eth} worth of eth deposited")
    print(f"you have {total_collateral_eth} worth of eth deposited")
    print(f"you have {total_debt_eth} worth of eth deposited")
    return (float(available_borrow_eth), float(total_debt_eth))


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_tx = approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("lets borrow")

    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"we are going to borrow {amount_dai_to_borrow}")

    dai_address = config["networks"][network.show_active()]["dai_token"] 
    borrow_tx = lending_pool.borrow(
        dai_address, Web3.toWei(amount_dai_to_borrow, "ether"), 
        1,
        0,
        account.address, {"from": account}
    )
    borrow_tx.wait(1)
    print("we borrowed some Dai jubii")
    get_borrowable_data(lending_pool, account)
    repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)
    print("i just deposited and repayed with link, brownie and aave")

def repay_all(amount, lending_pool, account):
    approve_erc20(Web3.toWei(amount, "ether"), lending_pool, config["networks"][network.show_active()]["dai_token"], account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"], amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("repayed")

def get_asset_price(price_data):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_data)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)
    



    
