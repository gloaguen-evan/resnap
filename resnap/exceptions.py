class ResnapError(Exception):
    def __init__(self, message: str, data: dict) -> None:
        self.message = message
        self.data = data
        super().__init__(self.message)
