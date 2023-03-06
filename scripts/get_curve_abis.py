from dotenv import load_dotenv, dotenv_values
import logging
import requests
import pandas as pd
import json
from web3 import Web3
from web3.providers.rpc import HTTPProvider

def connect():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    config = dotenv_values(".env")
    alchemy_project_id = config['WEB3_ALCHEMY_PROJECT_ID']
    alchemy_url = f'https://eth-mainnet.g.alchemy.com/v2/{alchemy_project_id}'
    provider = HTTPProvider(alchemy_url)
    web3 = Web3(provider)
    return(config)
    print(f'web3.eth: {web3.eth.block_number}')

def fetch_abi(config, pool_address):
    etherscan_abi_call = f'''https://api.etherscan.io/api?module=contract&action=getabi&address={pool_address}&apikey={config['ETHERSCAN_TOKEN']}'''
    r = requests.get(etherscan_abi_call)
    abi = r.json()['result']
    return(abi)

if __name__ == "__main__":
    config = connect()

    curve_pools_df = pd.read_csv('data/curve-pool-large.csv')
    for index, row in curve_pools_df.iterrows():
        abi = fetch_abi(config, row['address'])
        with open(f'abis/curve_{row["pool"]}_abi.json', 'w', encoding='utf-8') as f:
            json.dump(abi, f, ensure_ascii=False)

    # print(curve_pools_df)

