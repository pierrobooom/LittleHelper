from PySide6.QtCore import QObject, Signal

class InferenceWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, client, model, prompt, system):
        super().__init__()
        self.client = client
        self.model = model
        self.prompt = prompt
        self.system = system


    def run(self):
        try:
            response = self.client.generate(
                model=self.model,
                prompt=self.prompt,
                system=self.system
            )
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))
