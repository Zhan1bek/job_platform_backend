from rest_framework import permissions


class ResumePermission(permissions.BasePermission):
    """
    Доступ к резюме:
    - Соискатель видит только свои.
    - Работодатель — только откликнувшихся.
    - Админ — всех.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        job_seeker = (
            getattr(user, "job_seeker_profile", None)
            or getattr(user, "jobseeker", None)
        )
        if job_seeker:
            return obj.job_seeker_id == job_seeker.id

        if getattr(user, "company", None):
            return obj.job_seeker.applications.filter(
                vacancy__company=user.company
            ).exists()

        return False
