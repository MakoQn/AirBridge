from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from src.database.db_connection import SessionLocal
from src.database.models.auth import AppUser, Role
import bcrypt

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Registration")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(self.username)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        
        btn = QPushButton("Register")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)
        self.setLayout(layout)

    def register(self):
        u = self.username.text()
        e = self.email.text()
        p = self.password.text()
        if not u or not e or not p: return
        
        session = SessionLocal()
        try:
            if session.query(AppUser).filter((AppUser.username == u) | (AppUser.email == e)).first():
                QMessageBox.warning(self, "Error", "Username or Email taken")
                return
            
            hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
            role = session.query(Role).filter_by(role_name="Client").first()
            user = AppUser(username=u, email=e, password_hash=hashed)
            user.roles.append(role)
            session.add(user)
            session.commit()
            QMessageBox.information(self, "Success", "Registered")
            self.accept()
        finally:
            session.close()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirBridge Login")
        self.resize(300, 150)
        
        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_login = QPushButton("Login")
        btn_login.clicked.connect(self.check)
        btn_reg = QPushButton("Register (Client)")
        btn_reg.clicked.connect(lambda: RegisterDialog().exec())
        
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        h = QHBoxLayout()
        h.addWidget(btn_login)
        h.addWidget(btn_reg)
        layout.addLayout(h)
        self.setLayout(layout)
        self.user_data = None

    def check(self):
        u = self.username.text()
        p = self.password.text()
        
        session = SessionLocal()
        try:
            user = session.query(AppUser).filter_by(username=u).first()
            if user and user.check_password(p):
                if user.is_blocked:
                    QMessageBox.warning(self, "Error", "Account Blocked")
                    return
                
                role = "Superuser" if user.is_superuser else (user.roles[0].role_name if user.roles else "Client")
                self.user_data = {"id": user.id, "username": user.username, "role": role}
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
        finally:
            session.close()