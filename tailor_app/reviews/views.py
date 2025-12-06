from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        tailor_id = self.request.query_params.get('tailor_id')
        if tailor_id:
            return Review.objects.filter(order__tailor_id=tailor_id)
        # By default, maybe return all or none? Let's return all for now.
        return Review.objects.all()

    def perform_create(self, serializer):
        # Additional validation is handled in serializer
        serializer.save()
