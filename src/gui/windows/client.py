from PyQt6.QtWidgets import QLabel

class ClientWindow(QLabel):
    def __init__(self, user_id):
        super().__init__(f"Client Panel for ID {user_id} (Under Construction)")