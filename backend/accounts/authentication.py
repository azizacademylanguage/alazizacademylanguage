from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class TokenVersionJWTAuthentication(JWTAuthentication):
    """Parol almashtirilganda yoki barcha qurilmalardan chiqilganda eski JWTlarni bekor qiladi."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_version = int(validated_token.get('token_version', 1))
        if token_version != int(getattr(user, 'token_version', 1)):
            raise AuthenticationFailed('Sessiya bekor qilingan. Qayta kiring.', code='session_revoked')
        if not user.faol:
            raise AuthenticationFailed('Hisob faol emas.', code='user_inactive')
        return user
