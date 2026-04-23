from typing import Annotated

from fastapi import Depends

from balancer.config import Config, get_config

ConfigDI = Annotated[Config, Depends(get_config)]
