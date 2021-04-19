from django.db import models


class LockedNFT(models.Model):
    owner = models.CharField(max_length=50, unique=True)
    nftAddress = models.CharField(max_length=50)
    nftId = models.IntegerField()
