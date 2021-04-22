from django.conf import settings
from django.db import models
from web3 import Web3
from web3.middleware import geth_poa_middleware

from contract_abi import nft_lock_abi, bep20_abi

url = settings.NETWORK_SETTINGS['ETH_MAINNET']['url']
eth_rpc = Web3(Web3.HTTPProvider(url))
eth_rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

url = settings.NETWORK_SETTINGS['BSC_MAINNET']['url']
bsc_rpc = Web3(Web3.HTTPProvider(url))
bsc_rpc.middleware_onion.inject(geth_poa_middleware, layer=0)

unlock_contract = eth_rpc.eth.contract(address=eth_rpc.toChecksumAddress(settings.UNLOCK_ADDRESS), abi=nft_lock_abi)


class LockedNFT(models.Model):
    owner = models.CharField(max_length=50)
    nftAddress = models.CharField(max_length=50)
    nftId = models.IntegerField()
    bep20 = models.OneToOneField('BEP20', null=True, on_delete=models.CASCADE, related_name='nft')
    ready_to_withdraw = models.BooleanField(default=False)
    name = models.CharField(max_length=256, null=True)
    image_url = models.TextField(null=True)
    permalink = models.TextField(null=True)

    def unlock(self):
        if not self.ready_to_withdraw:
            return
        tx_params = {'gas': 70000,
                     'gasPrice': eth_rpc.eth.gasPrice,
                     'chainId': eth_rpc.eth.chainId,
                     'nonce': eth_rpc.eth.get_transaction_count(settings.PUBLIC_KEY),
                     'from': settings.PUBLIC_KEY
                     }
        tx = unlock_contract.functions.unlock(self.owner, self.nftAddress, self.nftId).buildTransaction(tx_params)
        signed_tx = eth_rpc.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
        print(signed_tx)
        tx_hash = eth_rpc.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(tx_hash.hex())
        self.delete()
        return tx_hash.hex()


class BEP20(models.Model):
    tokenAddress = models.CharField(max_length=50)
    created_from = models.CharField(max_length=50)
    current_balance = models.CharField(max_length=256)
    total = models.CharField(max_length=256)
    name = models.CharField(max_length=32)
    decimals = models.IntegerField(null=True)
    burned = models.BooleanField(default=False)

    def check_balance(self):
        contract = bsc_rpc.eth.contract(address=bsc_rpc.toChecksumAddress(self.tokenAddress), abi=bep20_abi)
        current_balance = contract.functions.balanceOf(contract.address).call()
        self.current_balance = current_balance
        self.save()

    def check_decimals(self):
        contract = bsc_rpc.eth.contract(address=bsc_rpc.toChecksumAddress(self.tokenAddress), abi=bep20_abi)
        decimals = contract.functions.decimals().call()
        total = contract.functions.totalSupply().call()
        name = contract.functions.name().call()
        self.decimals = decimals
        self.total = total
        self.name = name
        self.save()
