from rest_framework.generics import ListAPIView

from backend.locked_nft.models import LockedNFT
from backend.locked_nft.serializers import LockedNFTSerializer


class LockedNFTView(ListAPIView):
    serializer_class = LockedNFTSerializer
    queryset = LockedNFT.objects.all()
