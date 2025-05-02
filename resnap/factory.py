from .helpers.config import Config, Services
from .services.local_service import LocalResnapService
from .services.service import ResnapService
from .settings import get_config_data

_resnap_config: Config = get_config_data()
_service: ResnapService | None = None


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
        if _resnap_config.save_to == Services.LOCAL:
            _service = LocalResnapService(_resnap_config)
        elif _resnap_config.save_to == Services.S3:
            from .services.boto_service import BotoResnapService
            _service = BotoResnapService(_resnap_config)
        else:
            raise NotImplementedError(f"Resnap service {_resnap_config.save_to} is not implemented")
        return _service
