from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import ReviewSerializer
from ...models import ReviewModel, ReviewStatusType
from catalog.models import ProductModel


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = ReviewModel.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ReviewModel.objects.all()
        return ReviewModel.objects.filter(user=user, status=ReviewStatusType.accepted.value)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({"detail": "شما اجازه حذف این نظر را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({"detail": "شما اجازه ویرایش این نظر را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        
        # If the user is not staff, they can only edit their own reviews, and the status should not be changed
        if not request.user.is_staff:
            if 'status' in request.data:
                return Response({"detail": "شما مجاز به تغییر وضعیت نظر نیستید."}, status=status.HTTP_403_FORBIDDEN)
            # Prevent editing of description and rate if the review is already accepted
            if instance.status == ReviewStatusType.accepted.value:
                if 'description' in request.data or 'rate' in request.data:
                    return Response({"detail": "نظرات تایید شده قابل ویرایش نیستند."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().partial_update(request, *args, **kwargs)
