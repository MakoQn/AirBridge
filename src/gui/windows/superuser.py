from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView, QMessageBox, QComboBox, QLineEdit, QDialog, QFormLayout
from src.database.db_connection import SessionLocal
from src.database.models.auth import AppUser, Role
import bcrypt

class CreateStaffDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Staff")
        self.layout = QFormLayout()
        
        self.username = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["Administrator", "Dispatcher"])
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Role:", self.role)
        self.layout.addRow("Password:", self.password)
        
        btn = QPushButton("Create")
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)
        self.setLayout(self.layout)

class SuperuserWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        h = QHBoxLayout()
        btn_add = QPushButton("Create Staff")
        btn_add.clicked.connect(self.create_staff)
        btn_block = QPushButton("Block/Unblock")
        btn_block.clicked.connect(self.toggle_block)
        btn_del = QPushButton("Delete")
        btn_del.clicked.connect(self.delete_user)
        btn_ref = QPushButton("Refresh")
        btn_ref.clicked.connect(self.load_users)
        
        h.addWidget(btn_add)
        h.addWidget(btn_block)
        h.addWidget(btn_del)
        h.addWidget(btn_ref)
        layout.addLayout(h)
        
        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        session = SessionLocal()
        users = session.query(AppUser).filter(AppUser.is_superuser == False).all()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            role = u.roles[0].role_name if u.roles else "None"
            status = "Blocked" if u.is_blocked else "Active"
            self.table.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.table.setItem(i, 1, QTableWidgetItem(u.username))
            self.table.setItem(i, 2, QTableWidgetItem(role))
            self.table.setItem(i, 3, QTableWidgetItem(status))
        session.close()

    def create_staff(self):
        d = CreateStaffDialog()
        if d.exec():
            u = d.username.text()
            p = d.password.text()
            r_name = d.role.currentText()
            if not u or not p: return
            
            session = SessionLocal()
            try:
                if session.query(AppUser).filter_by(username=u).first():
                    QMessageBox.warning(self, "Error", "Exists")
                    return
                hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
                role = session.query(Role).filter_by(role_name=r_name).first()
                user = AppUser(username=u, email=f"{u}@staff.loc", password_hash=hashed)
                user.roles.append(role)
                session.add(user)
                session.commit()
                self.load_users()
            finally:
                session.close()

    def toggle_block(self):
        row = self.table.currentRow()
        if row < 0: return
        uid = int(self.table.item(row, 0).text())
        session = SessionLocal()
        u = session.get(AppUser, uid)
        u.is_blocked = not u.is_blocked
        session.commit()
        session.close()
        self.load_users()

    def delete_user(self):
        row = self.table.currentRow()
        if row < 0: return
        uid = int(self.table.item(row, 0).text())
        session = SessionLocal()
        u = session.get(AppUser, uid)
        session.delete(u)
        session.commit()
        session.close()
        self.load_users()