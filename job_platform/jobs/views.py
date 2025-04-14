# from rest_framework import viewsets, permissions
# from rest_framework import viewsets, filters
# from .models import Vacancy
# from .serializers import VacancySerializer
# from rest_framework.permissions import IsAuthenticatedOrReadOnly


# class VacancyViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy.objects.all()
#     serializer_class = VacancySerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#
#
# class VacancyViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy.objects.all()
#     serializer_class = VacancySerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['title', 'company__name']
#     ordering_fields = ['created_at']
