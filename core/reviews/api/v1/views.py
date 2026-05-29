from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import ReviewSerializer
from ...models import ReviewModel, ReviewStatusType
from ...permissions import IsOwnerOrAdmin
from catalog.models import ProductModel


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = ReviewModel.objects.all()
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete'
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ReviewModel.objects.all()
        return ReviewModel.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # If the user is not staff, they can only edit their own reviews, and the status should not be changed
        if not request.user.is_staff:
            if 'status' in request.data:
                return Response({"detail": "شما مجاز به تغییر وضعیت نظر نیستید."}, status=status.HTTP_403_FORBIDDEN)
            # Prevent editing of description and rate if the review is already accepted
            if instance.status == ReviewStatusType.accepted.value:
                if 'description' in request.data or 'rate' in request.data:
                    return Response({"detail": "نظرات تایید شده قابل ویرایش نیستند."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().partial_update(request, *args, **kwargs)
