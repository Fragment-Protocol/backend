from rest_framework import serializers

from backend.locked_nft.models import LockedNFT


class LockedNFTSerializer(serializers.ModelSerializer):
    class Meta:
        model = LockedNFT
        fields = '__all__'
