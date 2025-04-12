from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin
from litestar_saq import SAQPlugin

from app.config import app as config

structlog = StructlogPlugin(config=config.log)

saq = SAQPlugin(config=config.saq)
alchemy = SQLAlchemyPlugin(config=config.alchemy)
granian = GranianPlugin()
channels_backend = MemoryChannelsBackend(history=100)
channels_instance = ChannelsPlugin(backend=channels_backend, arbitrary_channels_allowed=True)
