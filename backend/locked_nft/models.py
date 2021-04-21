from django.conf import settings
from django.db import models
from web3 import Web3
from web3.middleware import geth_poa_middleware

from contract_abi import nft_lock_abi

url = settings.NETWORK_SETTINGS['ETH_MAINNET']['url']
rpc = Web3(Web3.HTTPProvider(url))
rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

unlock_contract = rpc.eth.contract(address=rpc.toChecksumAddress(settings.UNLOCK_ADDRESS), abi=nft_lock_abi)


class LockedNFT(models.Model):
    owner = models.CharField(max_length=50)
    nftAddress = models.CharField(max_length=50)
    nftId = models.IntegerField()
    bep20 = models.OneToOneField('BEP20', null=True, on_delete=models.CASCADE, related_name='bep20')
    ready_to_withdraw = models.BooleanField(default=False)
    name = models.CharField(max_length=256, null=True)
    image_url = models.TextField(null=True)
    permalink = models.TextField(null=True)

    def unlock(self):
        if not self.ready_to_withdraw:
            return
        tx = unlock_contract.functions.unlock(self.owner, self.nftAddress, self.nftId).buildTransaction()
        tx.update({'gas': 30000})
        tx.update({'gasPrice': rpc.eth.gasPrice})
        tx.update({'chainId': rpc.eth.chainId})
        tx.update({'nonce': rpc.eth.get_transaction_count(settings.PUBLIC_KEY)})
        signed_tx = rpc.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
        print(signed_tx)
        tx_hash = rpc.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(tx_hash.hex())
        return tx_hash.hex()


class BEP20(models.Model):
    tokenAddress = models.CharField(max_length=50)
    created_from = models.CharField(max_length=50)
    current_balance = models.CharField(max_length=256)
    total = models.CharField(max_length=256)
    name = models.CharField(max_length=32)
