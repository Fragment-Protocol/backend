from backend.locked_nft.models import LockedNFT


def create_locked_nft(message):
    l = LockedNFT(**message)
    l.save()
    return l
