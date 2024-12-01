from ..data_provider import DataProvider

class ProviderFactory:
    """
    Factory for managing data providers.
    """

    def __init__(self):
        # Register providers (only one for now, scalable later)
        self.providers = {
            "default": DataProvider(),
        }

    def get_provider(self, provider_name):
        """
        Retrieve a data provider by name.
        """
        return self.providers.get(provider_name, DataProvider())
