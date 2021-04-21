import os
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from backend.locked_nft.models import LockedNFT


def process():
    addresses = LockedNFT.objects.filter(bep20__isnull=False, bep20__burned=False)
    print(f'Check {len(addresses)} addresses')
    for address in addresses:
        address.bep20.check_balance()


if __name__ == '__main__':
    while True:
        process()
        time.sleep(60)
