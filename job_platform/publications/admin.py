from django.contrib import admin
from .models import (
    Publication,
    PostCategory,
    PublicationLike,
    Comment,
    CommentLike,
)

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'company', 'post_type', 'category', 'created_at')
    list_filter = ('post_type', 'category', 'company')
    search_fields = ('title', 'text', 'tags')
    autocomplete_fields = ('author', 'company', 'category')


@admin.register(PublicationLike)
class PublicationLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication', 'user', 'text', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
