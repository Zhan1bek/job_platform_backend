from rest_framework import permissions

class IsConversationParticipant(permissions.BasePermission):
    """
    Проверяет, является ли пользователь участником беседы
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли объект беседой или сообщением
        if hasattr(obj, 'participants'):  # Это беседа
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):  # Это сообщение
            return request.user in obj.conversation.participants.all()
        return False