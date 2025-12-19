from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel, QTabWidget
from src.services.backup_service import create_backup
from src.database.db_connection import SessionLocal
from src.database.models.auth import AppUser

class AdminWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        
        tab_bk = QWidget()
        v1 = QVBoxLayout()
        btn = QPushButton("Create Backup & Upload to Cloud")
        btn.clicked.connect(self.make_backup)
        v1.addWidget(btn)
        v1.addWidget(QLabel("Backups are stored in MinIO bucket 'avia-storage'"))
        tab_bk.setLayout(v1)
        self.addTab(tab_bk, "Backups")
        
        tab_st = QWidget()
        v2 = QVBoxLayout()
        self.lbl_stats = QLabel()
        btn_r = QPushButton("Refresh Stats")
        btn_r.clicked.connect(self.load_stats)
        v2.addWidget(self.lbl_stats)
        v2.addWidget(btn_r)
        tab_st.setLayout(v2)
        self.addTab(tab_st, "System Stats")
        
        self.load_stats()

    def make_backup(self):
        try:
            create_backup()
            QMessageBox.information(self, "Success", "Backup Created")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_stats(self):
        session = SessionLocal()
        cnt = session.query(AppUser).count()
        self.lbl_stats.setText(f"Total Users: {cnt}")
        session.close()