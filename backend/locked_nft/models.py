from django.db import models


class LockedNFT(models.Model):
    owner = models.CharField(max_length=50)
    nftAddress = models.CharField(max_length=50)
    nftId = models.IntegerField()
    bep20 = models.OneToOneField('BEP20', null=True, on_delete=models.CASCADE, related_name='bep20')


class BEP20(models.Model):
    tokenAddress = models.CharField(max_length=50, unique=True)
    created_from = models.CharField(max_length=50)
    current_balance = models.CharField(max_length=256)
    total = models.CharField(max_length=256)
