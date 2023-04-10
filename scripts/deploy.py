import time
from brownie import accounts, Lottery,config,network
from scripts.helpScripts import *


def deployLottery():
    account = get_account()
    # the first 5 parameters are the parameters of Lottery constructor
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from":account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lottery deployed!")
    return lottery

def startLottery():
    account=get_account()
    # get latest lottery
    lottery=Lottery[-1]
    lottery.startLottery({"from":account})
    print("The lottery is started!")

def enterLottery():
    account=get_account()
    lottery=Lottery[-1]
    entranceFee=lottery.getEntranceFee()+100
    tx=lottery.enter({"from":account,"value":entranceFee})
    tx.wait(1)
    print("enter lottery successfully!")

def endLottery():
    account=get_account()
    lottery=Lottery[-1]
    # we need to fund the contract with link token before end it(since we need to generate random number)
    tx=fund_with_link(lottery.address)
    tx.wait(1)
    endingTx=lottery.endLottery({"from":account})
    endingTx.wait(1)
    # wait for generating random number
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the winner!")

def main():
    deployLottery()
    startLottery()
    enterLottery()
    endLottery()
