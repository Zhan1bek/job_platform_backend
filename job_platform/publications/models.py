from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company

class Publication(models.Model):
    """
    Публикация (пост).
    Может быть создана:
    - обычным пользователем (job_seeker/employer)
    - либо "официально" от имени компании.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publications'
    )
    # Если хотим позволить постить "от имени компании"
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='publications'
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='publications/',
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.company:
            return f"Post by {self.company.name} (user: {self.author.username})"
        return f"Post by user {self.author.username}"


class PublicationLike(models.Model):
    """
    Лайк на публикацию. Один пользователь = один лайк
    Можно удалить (unlike), тогда запись пропадёт.
    """
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publication_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('publication', 'user'),)

    def __str__(self):
        return f"Like by {self.user.username} on {self.publication.id}"


class Comment(models.Model):
    """
    Комментарий к публикации. Поддерживает вложенность (ответ на другой коммент).
    """
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.publication.id}"


class CommentLike(models.Model):
    """
    Лайк на комментарий. Аналогично - 1 пользователь = 1 лайк
    """
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('comment', 'user'),)

    def __str__(self):
        return f"Like by {self.user.username} on comment {self.comment.id}"
