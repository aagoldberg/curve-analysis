from brownie import network, accounts, Contract, chain
import brownie
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from dotenv import load_dotenv
import logging
import json
from pandas.io.json import json_normalize
import requests
import pandas as pd
import csv
import pickle

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
load_dotenv()

# connect through brownie
NETWORK = "alchemynode"
network.connect(NETWORK)
logging.info(f"Network {NETWORK} is connected: %s", network.is_connected())
brownie.network.multicall.CONFIG.active_network['multicall2'] = '0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696'

#connect through web3.py
api_url = brownie.network.multicall.CONFIG.active_network['host']
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_token_supply_block_history(pool_address, brownie_pool, start_block, end_block):
    
    tokenSupply_dict = {}

    for block in range(start_block, end_block+1, 3238):
        tokenSupply_dict[block] = {}
        
        web3.eth.default_block = block
        if str(web3.eth.getCode(pool_address)) != "b''":

            with brownie.multicall(block_identifier=block):
                tokenSupply_dict[block]['totalSupply'] = brownie_pool.totalSupply()
                tokenSupply_dict[block]['timeStamp'] = chain[block].timestamp
                print(f'block: {block}, timestamp: {tokenSupply_dict[block]["timeStamp"]}, totalSupply: {tokenSupply_dict[block]["totalSupply"]}')

        else: print(f'contract doesnt exist at block {block}')

    return(tokenSupply_dict)


def main():

    start_block = 12525700
    end_block = 14309926

    pool_address = '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B'

    # instantiate brownie pool 
    with open("../abis/ConvexToken.json") as f: abi = json.load(f)
    cvx_pool = Contract.from_abi("pool", pool_address, abi)

    # get virtual price history per block, save to pandas dataframe
    cvx_token_dict = get_token_supply_block_history(pool_address, cvx_pool, start_block, end_block)
    cvx_tokensupply_df = pd.DataFrame.from_dict(cvx_token_dict, orient='index')

    cvx_tokensupply_df.to_csv(f'../data/cvx_token_supply/cvx_tokensupply_{start_block}_{end_block}.csv')

if __name__ == "__main__":
    main()