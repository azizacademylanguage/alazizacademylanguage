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
        user = request.user
        if not (user and user.is_authenticated and user.role == 'oquvchi'):
            return False
        # Muddati tugagan o'quvchi login qila oladi, ammo ta'lim va o'yin API'lari
        # qulflanadi. Bildirishnoma/coin holatini ko'rish uchun ayrim yo'llar ochiq.
        if getattr(user, 'muddat_tugagan', False):
            allowed = ('bildirishnomalar', 'coinlarim', 'shop-buyurtmalarim', 'streak')
            if not any(part in request.path for part in allowed):
                self.message = "Foydalanish muddati tugagan. Davom ettirish uchun admin bilan bog'laning."
                return False
        return True


class IsOwnerNazoratchi(BasePermission):
    message = "Siz faqat o'zingiz yaratgan o'quvchilarni boshqara olasiz."

    def has_object_permission(self, request, view, obj):
        return obj.yaratgan_id == request.user.id
