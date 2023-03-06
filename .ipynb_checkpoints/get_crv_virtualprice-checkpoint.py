from brownie import network, accounts, Contract, chain
import brownie
from brownie import web3
# from web3 import Web3
# from web3.providers.rpc import HTTPProvider
from dotenv import load_dotenv
import logging
import json
from pandas.io.json import json_normalize
import requests
import pandas as pd
import csv
import pickle

def connect():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    load_dotenv()

    # connect through brownie
    NETWORK = "alchemynode"
    network.connect(NETWORK)
    logging.info(f"Network {NETWORK} is connected: %s", network.is_connected())
    brownie.network.multicall.CONFIG.active_network['multicall2'] = '0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696'

    #connect through web3.py
    # api_url = brownie.network.multicall.CONFIG.active_network['host']
    # provider = HTTPProvider(api_url)
    # web3 = Web3(provider)

def get_virtual_price_block_history(pool_address, brownie_pool, start_block, end_block):

    virtualprice_dict = {}

    for block in range(start_block, end_block+1, 3238):
        virtualprice_dict[block] = {}

        web3.eth.default_block = block
        if str(web3.eth.getCode(pool_address)) != "b''":

            with brownie.multicall(block_identifier=block):
                virtualprice_dict[block]['virtualPrice'] = brownie_pool.get_virtual_price()
                virtualprice_dict[block]['timeStamp'] = chain[block].timestamp
                print(f'block: {block}, timestamp: {virtualprice_dict[block]["timeStamp"]}, virtualPrice: {virtualprice_dict[block]["virtualPrice"]}')
        
        else: print(f'contract doesnt exist at block {block}')

    return(virtualprice_dict)


def main(start_block, end_block):

    with open('../data/convex_addresses.json') as json_data: convex_json = json.load(json_data)
    convex_pools_df = pd.DataFrame(convex_json['pools'])[['swap', 'name']]

    # change these, and keep them the SAME as in 'get_csv_rewardRate.py' and 'get_cvx_token_supply.py'!!
    # start_block = 11972002
    start_block = start_block
    end_block = end_block

    # retreive pool stableswap address
    # pool_address_csv = '../data/curve_pool_name_address.csv'
    # pool_address_list = pd.read_csv(pool_address_csv)

    # completed_pools: frax, normies, ousd, wormhole, ironbank, wormhole, mim, fei
    #n nonstandard: wormhole
    target_pools = ['alusd', 'susd', 'frax', 'mim', 'ousd', 'ironbank', 'fei', 'ust-wormhole']
    for pool in target_pools:

            pool_address = convex_pools_df.loc[convex_pools_df.name == pool, 'swap'].values[0]
            # pool_address = pool_address_list.loc[pool_address_list.curve_pool == pool, 'address'].values[0]
            print(f'pool: {pool}, pool address: {pool_address}')

            # instantiate brownie pool 
            with open("../abis/StableSwap.json") as f: abi = json.load(f)
            crv_pool = Contract.from_abi("pool", pool_address, abi)

            # get virtual price history per block, save to pandas dataframe
            pool_virtualprice_dict = get_virtual_price_block_history(pool_address, crv_pool, start_block, end_block)
            pool_virtualprice_df = pd.DataFrame.from_dict(pool_virtualprice_dict, orient='index')
            print(pool_virtualprice_df.head(1))
            pool_virtualprice_df.index.name = 'block'
            print(pool_virtualprice_df.head(1))

            # pool_virtualprice_df = pool_virtualprice_df.reset_index()

            pool_virtualprice_df.to_csv(f'../data/virtualPrice/{pool}/virtualPrice_{pool}_{start_block}_{end_block}.csv')

# if __name__ == "__main__":
#     main()