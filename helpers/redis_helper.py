import aioredis


class RedisSession:
    """Wrapper class to share a connection pool across application."""

    _pool = None

    async def get_redis_pool(self):
        """Return existing connection from connection Pool else return new Connecton from Pool."""
        if not self._pool:
            self._pool = await aioredis.create_pool(
                address="redis://redis:6379/0"
            )
        return self._pool

    async def get_redis_obj(self):
        """Creates a redis object from the pool that we created above.

        NOTE: If using this function, don't forget to add redis_obj.close() to close the connection.
        """
        redis_pool = await self.get_redis_pool()
        return await aioredis.Redis(redis_pool)
