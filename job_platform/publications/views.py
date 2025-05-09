from .models import Publication, PublicationLike
from .serializers import PublicationSerializer, PublicationLikeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentLikeSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # user = request.user, publication - из validated_data
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='like')
    def like_comment(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if CommentLike.objects.filter(comment=comment, user=user).exists():
            return Response({"detail": "You already liked this comment"}, status=status.HTTP_400_BAD_REQUEST)
        CommentLike.objects.create(comment=comment, user=user)
        return Response({"detail": "Comment liked!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='like')
    def unlike_comment(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        like = CommentLike.objects.filter(comment=comment, user=user).first()
        if not like:
            return Response({"detail": "You have not liked this comment"}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({"detail": "Comment unliked!"}, status=status.HTTP_204_NO_CONTENT)


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post_type', 'company', 'category', 'author']
    search_fields = ['text', 'title', 'tags']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Заполняем author = self.request.user.
        Если передан company_id — проверяем, что пользователь
        имеет право постить от её имени (user.company == that company).
        """
        user = self.request.user
        company = serializer.validated_data.get('company', None)
        if company:
            # проверяем, что user может постить от имени этой company
            # напр. user.company == company или user.role='employer'
            if user.role != 'employer' or user.company != company:
                raise PermissionError("You can't post on behalf of this company")
        serializer.save(author=user)

    @action(detail=True, methods=['post'], url_path='like')
    def like_publication(self, request, pk=None):
        """
        POST /publications/<pk>/like/ – поставить лайк,
        если лайк уже есть – вернём ошибку 400
        """
        publication = self.get_object()
        user = request.user
        # проверяем, что не поставил лайк раньше
        like_exist = PublicationLike.objects.filter(publication=publication, user=user).exists()
        if like_exist:
            return Response({"detail": "You already liked this publication"}, status=status.HTTP_400_BAD_REQUEST)
        like = PublicationLike.objects.create(publication=publication, user=user)
        return Response({"detail": "Liked!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='like')
    def unlike_publication(self, request, pk=None):
        """
        DELETE /publications/<pk>/like/ – убрать лайк
        """
        publication = self.get_object()
        user = request.user
        like = PublicationLike.objects.filter(publication=publication, user=user).first()
        if not like:
            return Response({"detail": "You have not liked this publication"}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({"detail": "Unliked!"}, status=status.HTTP_204_NO_CONTENT)
