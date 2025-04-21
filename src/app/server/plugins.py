from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.channels import ChannelsPlugin

# from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.backends.redis import RedisChannelsStreamBackend

from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin
from litestar_saq import SAQPlugin
from app.config import app as config
from app.config.base import get_settings

settings = get_settings()

structlog = StructlogPlugin(config=config.log)

saq = SAQPlugin(config=config.saq)
alchemy = SQLAlchemyPlugin(config=config.alchemy)
granian = GranianPlugin()


redis_client = settings.redis.get_client()


redis_backend = RedisChannelsStreamBackend(redis=redis_client, history=100, stream_ttl=3600)

channels_plugin = ChannelsPlugin(
    backend=redis_backend,
    arbitrary_channels_allowed=True,
)

# channels_instance = ChannelsPlugin(backend=MemoryChannelsBackend(history=100), arbitrary_channels_allowed=True)
