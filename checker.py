import os

from web3 import Web3
from web3.middleware import geth_poa_middleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.conf import settings

from backend.locked_nft.models import LockedNFT
from contract_abi import bep20_abi

url = settings.NETWORK_SETTINGS['BSC_MAINNET']['url']
rpc = Web3(Web3.HTTPProvider(url))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)


def process():
    addresses = LockedNFT.objects.all()
    for address in addresses:
        contract = rpc.eth.contract(address=rpc.toChecksumAddress('0x2170ed0880ac9a755fd29b2688956bd959f933f8'),
                                    abi=bep20_abi)
        current_balance = contract.functions.balanceOf(contract.address).call()
        total = contract.functions.totalSupply().call()
        address.bep20.current_balance = current_balance
        address.bep20.total = total


if __name__ == '__main__':
    process()
