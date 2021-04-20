from rest_framework import serializers

from backend.locked_nft.models import LockedNFT, BEP20


class BEP20Serializer(serializers.ModelSerializer):
    class Meta:
        model = BEP20
        fields = '__all__'


class LockedNFTSerializer(serializers.ModelSerializer):
    bep20 = BEP20Serializer()

    class Meta:
        model = LockedNFT
        fields = '__all__'
