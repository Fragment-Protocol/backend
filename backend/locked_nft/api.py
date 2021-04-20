from backend.locked_nft.models import LockedNFT, BEP20


def create_locked_nft(message):
    l = LockedNFT(**message)
    l.save()
    return l


def create_bep20(message):
    message['created_from'] = message.pop('from')
    o = BEP20(**message)
    o.save()
    return o
