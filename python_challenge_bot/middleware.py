# based on this source: https://gist.github.com/AliRn76/1fb99688315bedb2bf32fc4af0e50157 , with adaptations
# and based on this thread: https://gist.github.com/rluts/22e05ed8f53f97bdd02eafdf38f3d60a
import re

from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token_key = None
        for header in scope['headers']:
            if header[0].decode() == 'authorization':
                token_match = re.match('Token (.*)', header[1].decode())
                if token_match:
                    token_key = token_match.groups()[0]
        if token_key is not None:
            scope['user'] = await get_user(token_key)
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
