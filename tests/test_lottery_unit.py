from brownie import accounts, Lottery, config, network,exceptions
from web3 import Web3
from scripts.deploy import *
from scripts.helpScripts import *
import pytest
from brownie import *

def testGetEntranceFee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery=deployLottery()
    entranceFee=lottery.getEntranceFee()
    # 50USD=0.025 wei ether
    assert entranceFee==Web3.toWei(0.025,"ether")

def testCannotEnterUnlessStart():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery=deployLottery()
    with pytest.raises(exceptions.VirtualMachineError):
        account=get_account()
        entranceFee=lottery.getEntranceFee()
        # in test, we don't need to wait for completing contract
        lottery.enter({"from":account,"value":entranceFee})

def testStartAndEnter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery=deployLottery()
    account=get_account()
    lottery.startLottery({"from":account})
    entranceFee=lottery.getEntranceFee()
    lottery.enter({"from":account,"value":entranceFee})
    # use () but not [] to subscript array in solidity
    assert lottery.players(0)==account

def testEnd():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery=deployLottery()
    account=get_account()
    lottery.startLottery({"from":account})
    entranceFee=lottery.getEntranceFee()
    lottery.enter({"from":account,"value":entranceFee})
    # add .address or not is OK
    fund_with_link(lottery.address)
    lottery.endLottery({"from":account})
    # use () to get variable in solidity
    assert lottery.lotteryState()==2

def testGetAccount():
    account=get_account(index=1)

def testPickWinnerCorrectly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery=deployLottery()
    account=get_account()
    lottery.startLottery({"from":account})
    entranceFee=lottery.getEntranceFee()
    lottery.enter({"from":account,"value":entranceFee})
    lottery.enter({"from":get_account(index=1),"value":entranceFee})
    lottery.enter({"from":get_account(index=2),"value":entranceFee})
    fund_with_link(lottery)
    startingBalance=account.balance()
    txn=lottery.endLottery({"from":account})
    requestId=txn.events["RequestedRandomness"]["requestId"]
    # set the result of random number
    RANDOM_NUMBER=778
    get_contract("vrf_coordinator").callBackWithRandomness(requestId,RANDOM_NUMBER,lottery.address,{"from":account})
    time.sleep(1)
    # 777%3=0 and acconts[0]=account
    here
    assert lottery.recentWinner()==account
    lotteryBalance=lottery.balance()
    assert lotteryBalance==0
    assert startingBalance+lotteryBalance==account.balance()