import json
from pathlib import Path

with Path('contract_abi', 'erc20_abi.json').open() as f:
    bep20_abi = json.load(f)
with Path('contract_abi', 'factory_abi.json').open() as f:
    factory = json.load(f)
with Path('contract_abi', 'nft_lock.json').open() as f:
    nft_lock_abi = json.load(f)
