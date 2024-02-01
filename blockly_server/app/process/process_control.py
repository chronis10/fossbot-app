class ProcessManager:
    _instance = None
    _process = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_process(self, process):
        self._process = process

    def get_process(self):
        return self._process