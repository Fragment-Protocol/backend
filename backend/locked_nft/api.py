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
    print(f'created nft with id {l.id}')
    url = 'https://api.opensea.io/api/v1/asset/{0}/{1}/'
    r = get(url.format(nftAddress, nftId))
    if not r.status_code == 404:
        data = r.json()
        l.name = data.get('name')
        l.image_url = data.get('image_url')
        l.permalink = data.get('permalink')
        l.save()
    bep20 = BEP20.objects.filter(nft__isnull=True, burned=False).last()
    if not bep20:
        print(f'BEP20 not found for token with id {l.id}')
        return l
    l.bep20 = bep20
    l.save()
    return l


def create_bep20(message):
    tokenAddress = message['tokenAddress']
    created_from = message['from']
    o = BEP20(tokenAddress=tokenAddress, created_from=created_from)
    o.save()
    o.check_balance()
    o.check_decimals()
    print(f'created bsc20 with id {o.id}')
    locked_nft = LockedNFT.objects.filter(owner__iexact=created_from, bep20__isnull=True).first()
    if not locked_nft:
        print(f'NFT not found with owner {created_from}')
        return o
    locked_nft.bep20 = o
    locked_nft.save()
    return o


def unlock_nft(message):
    print(f'Start unlocking {message}')
    tokenAddress = message.get('tokenAddress')
    o = LockedNFT.objects.get(bep20__tokenAddress=tokenAddress)
    o.unlock()
    o.ready_to_withdraw = True
    o.save()
    o.bep20.burned = True
    o.bep20.current_balance = o.bep20.total
    o.bep20.save()
