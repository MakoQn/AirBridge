from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from src.database.db_connection import SessionLocal
from src.database.models.auth import AppUser, Role
import bcrypt

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(350, 250)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Придумайте имя пользователя")
        layout.addWidget(self.username)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        layout.addWidget(self.email)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        btn_reg = QPushButton("Зарегистрироваться")
        btn_reg.clicked.connect(self.register)
        layout.addWidget(btn_reg)

        self.setLayout(layout)

    def register(self):
        user = self.username.text()
        email = self.email.text()
        pwd = self.password.text()

        if not user or not pwd or not email:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны")
            return

        session = SessionLocal()
        try:
            if session.query(AppUser).filter((AppUser.username == user) | (AppUser.email == email)).first():
                QMessageBox.warning(self, "Ошибка", "Имя пользователя или Email уже заняты")
                return

            hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            client_role = session.query(Role).filter_by(role_name="Client").first()
            
            new_user = AppUser(username=user, email=email, password_hash=hashed)
            new_user.roles.append(client_role)
            
            session.add(new_user)
            session.commit()
            
            QMessageBox.information(self, "Успех", "Аккаунт создан! Теперь можно войти")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirBridge")
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout()
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Имя пользователя")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self.check_login)
        
        btn_reg = QPushButton("Регистрация")
        btn_reg.clicked.connect(self.open_register)
        
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        
        btns = QHBoxLayout()
        btns.addWidget(btn_login)
        btns.addWidget(btn_reg)
        layout.addLayout(btns)
        
        self.setLayout(layout)
        self.user_data = None

    def check_login(self):
        login = self.username.text()
        pwd = self.password.text()
        
        session = SessionLocal()
        try:
            user = session.query(AppUser).filter_by(username=login).first()
            if user and user.check_password(pwd):
                if user.is_blocked:
                    QMessageBox.warning(self, "Ошибка", "Аккаунт заблокирован")
                    return
                
                role_name = "Superuser" if user.is_superuser else (user.roles[0].role_name if user.roles else "Client")
                self.user_data = {
                    "id": user.id,
                    "username": user.username,
                    "role": role_name
                }
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Сбой входа: {e}")
        finally:
            session.close()

    def open_register(self):
        reg_win = RegisterDialog()
        reg_win.exec()