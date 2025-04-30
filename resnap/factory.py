from .helpers.config import Config, Services
from .services.local_service import LocalResnapService
from .services.service import ResnapService
from .settings import get_config_data


_resnap_config: Config = get_config_data()


class ResnapServiceFactory:
    @classmethod
    def get_service(cls) -> ResnapService:
        """
        Get resnap service based on the configuration.

        Returns:
            ResnapService: Resnap service.
        """
        if _resnap_config.save_to == Services.LOCAL:
            return LocalResnapService(_resnap_config)
        else:
            raise NotImplementedError(f"Resnap service {_resnap_config.save_to} is not implemented")
