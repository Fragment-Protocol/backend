from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from backend.locked_nft.models import LockedNFT
from backend.locked_nft.serializers import LockedNFTSerializer


class LockedNFTView(ListAPIView):
    serializer_class = LockedNFTSerializer
    queryset = LockedNFT.objects.all()


class UnlockNFTView(GenericAPIView):
    queryset = LockedNFT.objects.all()
    serializer_class = LockedNFTSerializer

    def post(self, request, *args, **kwargs):
        o = self.get_object()
        o.delete()
        return Response()
