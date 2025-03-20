from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin
from litestar_saq import SAQPlugin

from app.config import app as config
from app.lib.oauth import OAuth2ProviderPlugin

structlog = StructlogPlugin(config=config.log)
 
saq = SAQPlugin(config=config.saq)
alchemy = SQLAlchemyPlugin(config=config.alchemy)
granian = GranianPlugin()
oauth = OAuth2ProviderPlugin()
