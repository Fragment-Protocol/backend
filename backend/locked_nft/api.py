from django.conf import settings
from web3 import Web3
from web3.middleware import geth_poa_middleware

from backend.locked_nft.models import LockedNFT, BEP20
from contract_abi import nft_lock_abi
from requests import get

url = settings.NETWORK_SETTINGS['ETH_MAINNET']['url']
rpc = Web3(Web3.HTTPProvider(url))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

unlock_contract = rpc.eth.contract(address=rpc.toChecksumAddress(settings.UNLOCK_ADDRESS), abi=nft_lock_abi)


def create_locked_nft(message):
    owner = message['owner']
    nftAddress = message['nftAddress']
    nftId = message['nftId']
    l = LockedNFT(owner=owner, nftAddress=nftAddress, nftId=nftId)
    l.save()

    url = 'https://api.opensea.io/api/v1/asset/{0}/{1}/'
    r = get(url.format(nftAddress, nftId))
    if not r.status_code == 404:
        data = r.json()
        l.name = data.get('name')
        l.image_url = data.get('image_url')
        l.permalink = data.get('permalink')
    return l


def create_bep20(message):
    tokenAddress = message['tokenAddress']
    created_from = message['from']
    o = BEP20(tokenAddress=tokenAddress, created_from=created_from)
    o.save()
    return o


def unlock_nft(message):
    tokenAddress = message.get('tokenAddress')
    o = LockedNFT.objects.get(bep20__tokenAddress=tokenAddress)
    o.ready_to_withdraw = True
    o.save()
