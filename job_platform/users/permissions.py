from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS это GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        # Здесь obj – это наш Resume.
        # Сравним obj.job_seeker.user == request.user
        return obj.job_seeker.user == request.user
