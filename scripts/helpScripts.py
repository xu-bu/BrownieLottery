from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

# run "brownie accounts list" to list all accounts, then u can see the id
def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contractType=contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contractType)<=0:
            deploy_mocks()
        # get latest contract, similar to contract=MockV3Aggregator[-1]
        contract=contractType[-1]
    else:
        contractAddress=config["networks"][network.show_active()][contract_name]
        # if not test locally, create contract on mainnet, the 3 parameters are:
        # 1. name of contract
        # 2. address of contract
        # 3. abi of contract
        # contractType._name==str(contractType)
        contract=Contract.from_abi(contractType._name,contractAddress,contractType.abi)
    return contract



DECIMALS = 8
# we mock 1Wei ETH=2000 USD
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    gas_strategy = LinearScalingStrategy("60 gwei", "70 gwei", 1.1)
    gas_price(gas_strategy)
    account = get_account()
    # contructor parameters can be finding in /contracts/test/xxxxxx.sol, just follow it to deploy these components
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account, "gas_price": gas_strategy})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # users pay 0.1 Link as funding
    account=account if account else get_account()
    linkToken=link_token if link_token else get_contract("link_token")
    # use user's linkToken to fund VRF, therefore we can get the random number
    tx=linkToken.transfer(contract_address,amount,{"from":account})
    
    # alternative way to interact contract by using interface
    # linkTokenContract=interface.LinkTokenInterface(link_token.address)
    # tx=linkTokenContract.transfer(contract_address,amount,{"from":account})
    tx.wait(1)
    print("Fund contract!")
    return tx