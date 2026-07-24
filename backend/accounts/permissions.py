from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Bu amal faqat Admin uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsNazoratchi(BasePermission):
    message = "Bu amal faqat Nazoratchi uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'nazoratchi')


class IsOquvchi(BasePermission):
    message = "Bu amal faqat O'quvchi uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'oquvchi')


class IsOwnerNazoratchi(BasePermission):
    """Nazoratchi faqat o'zi yaratgan o'quvchilarga ega bo'lishi mumkin"""
    message = "Siz faqat o'zingiz yaratgan o'quvchilarni boshqara olasiz."

    def has_object_permission(self, request, view, obj):
        return obj.yaratgan_id == request.user.id
