from rest_framework import permissions

class IsCompanyOwner(permissions.BasePermission):
    """
    Permission: only the company.creator (created_by) can create jobs for that company.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # obj is Company when used on Company viewset, or Job when used on Job object
        user = request.user
        if isinstance(obj, type) and obj is None:
            return False
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == user
       
        if hasattr(obj, 'company'):
            return obj.company.created_by == user
        return False
