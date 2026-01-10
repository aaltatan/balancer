from typing import Annotated

from fastapi import Depends

from app.core.config import Config, get_config

ConfigDI = Annotated[Config, Depends(get_config)]
