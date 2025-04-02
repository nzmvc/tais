from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):  # Custom permission


    
    message = "You must be the owner of this object."
    def has_object_permission(self, request, view, obj):
        #print("isOwner has_object_permission çalıştı")
        return obj.open_user == request.user or request.user.is_superuser   # objenin sahibi veya admin isin yapabilir.
