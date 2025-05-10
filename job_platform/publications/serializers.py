from rest_framework import serializers
from .models import Publication, PublicationLike, Comment, CommentLike
from .models import PostCategory

class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name']

class PublicationSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(slug_field="name", queryset=PostCategory.objects.all(), required=False)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Publication
        fields = [
            'id', 'author', 'author_name', 'company', 'title', 'text', 'post_type',
            'tags', 'image', 'category',
            'created_at', 'updated_at',
            'likes_count', 'comments_count'
        ]
        read_only_fields = [
            'author', 'created_at', 'updated_at',
            'likes_count', 'comments_count'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # заполнить счётчики, если нужно
        data['likes_count'] = instance.likes.count()
        data['comments_count'] = instance.comments.count()
        return data


class CommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'publication', 'user', 'text', 'parent',
            'created_at', 'likes_count', 'replies'
        ]
        read_only_fields = ['user', 'created_at', 'likes_count']

    def get_replies(self, obj):
        # Рекурсивно показывать ответы? Или только 1 уровень
        serializer = CommentSerializer(obj.replies.all(), many=True)
        return serializer.data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['likes_count'] = instance.likes.count()
        return data


class PublicationLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationLike
        fields = ['id', 'publication', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'comment', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']
