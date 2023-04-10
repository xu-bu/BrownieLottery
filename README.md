# Function:

1. Users can enter lottery with ETH based on a USD fee
2. An admin will choose when the lottery is over
3. The lottery will select a random winner

# Configuration:
1. create .env:
example:

```
export WEB3_INFURA_PROJECT_ID=(get it from infura API keys)

export PRIVATE_KEY=(get it from metamask's account)

export ETHERSCAN_TOKEN=(variable name must be this, get it from ethescan-API keys, used for verification and deploying)
```
2. make sure you have enough Sepolia test ETH on your account (faucet link:`https://www.infura.io/faucet`), and enough LINK (faucet link:`https://faucets.chain.link/`)

# Usage:

run `brownie.exe run .\scripts\deploy.py --network sepolia`

# TODO:

Currently VRFv1 is deprecated and doesn't support sepolia, need to use VRFv2
