import os

from .helpers.config import Config, Services
from .services.local_service import LocalResnapService
from .services.service import ResnapService
from .settings import get_config_data

_resnap_config: Config | None = None
_service: ResnapService | None = None

_CONFIG_FILE_PATH_ENV_VAR = "RESNAP_CONFIG_FILE"


def get_config() -> Config:
    """Return a unique instance of the configuration, even if called multiple times.

    Returns:
        config (Config): The configuration singleton.
    """
    global _resnap_config
    if _resnap_config is None:
        file_path: str | None = os.getenv(_CONFIG_FILE_PATH_ENV_VAR)
        _resnap_config = get_config_data(file_path)
    return _resnap_config


def set_resnap_service(service: ResnapService) -> None:
    """
    Set the resnap service.

    Args:
        service (ResnapService): Resnap service.
    """
    if not isinstance(service, ResnapService):
        raise TypeError(f"Expected ResnapService, got {type(service)}")
    global _service
    _service = service


class ResnapServiceFactory:
    @classmethod
    def get_service(cls) -> ResnapService:
        """
        Get resnap service based on the configuration.

        Returns:
            ResnapService: Resnap service.
        """
        global _service
        if _service is not None:
            return _service

        config = get_config()
        if config.save_to == Services.LOCAL:
            _service = LocalResnapService(config)
        elif config.save_to == Services.S3:
            from .services.boto_service import BotoResnapService
            _service = BotoResnapService(config)
        else:
            raise NotImplementedError(f"Resnap service {config.save_to} is not implemented")
        return _service
