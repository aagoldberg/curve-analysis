from brownie import network, accounts, Contract, chain
import brownie
from brownie import web3
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
# api_url = brownie.network.multicall.CONFIG.active_network['host']
# provider = HTTPProvider(api_url)
# web3 = Web3(provider)

def get_rewards_supply_cvx(pool_address, brownie_pool, start_block, end_block):

    rewardRate_dict = {}

    # blocks_day = 6476 (https://ycharts.com/indicators/ethereum_blocks_per_day)
    # 2 blocks/day = 3238
    for block in range(start_block, end_block+1, 3238):
        rewardRate_dict[block] = {}

        web3.eth.default_block = block
        if str(web3.eth.getCode(pool_address)) != "b''":

            with brownie.multicall(block_identifier=block):
                rewardRate_dict[block]['rewardRate'] = brownie_pool.rewardRate()
                rewardRate_dict[block]['totalSupply'] = brownie_pool.totalSupply()
                rewardRate_dict[block]['timeStamp'] = chain[block].timestamp
                print(f'block: {block}, timestamp: {rewardRate_dict[block]["timeStamp"]}, rewardRate: {rewardRate_dict[block]["rewardRate"]}, totalSupply: {rewardRate_dict[block]["totalSupply"]}')
            # print(pd.DataFrame.from_dict(rewardRate_dict[block], orient='index').head(2))
        
        else: print(f'contract doesnt exist at block {block}')
    
    return(rewardRate_dict)


def main(start_block, end_block):

    with open('../data/convex_addresses.json') as json_data: convex_json = json.load(json_data)
    convex_pools_df = pd.DataFrame(convex_json['pools'])[['crvRewards', 'name', 'firstblock']]

    # start_block = 12525700
    # end_block = 14309926

    target_pools = ['alusd', 'susd', 'frax', 'mim', 'ousd', 'ironbank', 'fei', 'ust-wormhole']
    # target_pools = ['ust-wormhole']

    for pool in target_pools:
        print(pool)
        print(convex_pools_df.loc[convex_pools_df.name == pool, 'crvRewards'])
        pool_address = convex_pools_df.loc[convex_pools_df.name == pool, 'crvRewards'].values[0]
        print(f'pool: {pool}, pool address: {pool_address}')

        # instantiate brownie pool 
        with open("../abis/BaseRewardPool.json") as f: abi = json.load(f)
        crv_pool = Contract.from_abi("pool", pool_address, abi)

        # get reward rate and total supply history per block, save to pandas dataframe
        pool_rewardRate_dict = get_rewards_supply_cvx(pool_address, crv_pool, start_block, end_block)
        pool_rewards_supply_df = pd.DataFrame.from_dict(pool_rewardRate_dict, orient='index')
        pool_rewards_supply_df.index.name = 'block'
        pool_rewards_supply_df = pool_rewards_supply_df.reset_index()

        pool_rewards_supply_df.to_csv(f'../data/rewardRate_totalSupply/{pool}/{pool}_{start_block}_{end_block}.csv', index=False)

    network.disconnect(NETWORK)

# if __name__ == "__main__":
#     main()