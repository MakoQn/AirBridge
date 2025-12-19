import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from src.gui.windows.login import LoginDialog
from src.gui.windows.superuser import SuperuserWindow
from src.gui.windows.admin import AdminWindow
from src.gui.windows.dispatcher import DispatcherWindow
from src.gui.windows.client import ClientWindow

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user = user_data
        self.setWindowTitle(f"AirBridge - {user_data['role']}")
        self.resize(1000, 700)
        
        if user_data['role'] == "Superuser":
            self.setCentralWidget(SuperuserWindow())
        elif user_data['role'] == "Administrator":
            self.setCentralWidget(AdminWindow())
        elif user_data['role'] == "Dispatcher":
            self.setCentralWidget(DispatcherWindow())
        elif user_data['role'] == "Client":
            self.setCentralWidget(ClientWindow(user_data['id']))
        else:
            self.setCentralWidget(QLabel("Unknown Role"))

def main():
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec():
        w = MainWindow(login.user_data)
        w.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()