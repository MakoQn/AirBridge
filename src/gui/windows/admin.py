from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel, 
    QTabWidget, QSpacerItem, QSizePolicy
)
from src.services.backup_service import create_backup
from src.database.db_connection import SessionLocal
from src.database.models.auth import AppUser

class AdminWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        
        tab_bk = QWidget()
        v1 = QVBoxLayout()
        btn = QPushButton("Создание резервной копии")
        btn.clicked.connect(self.make_backup)
        v1.addWidget(btn)
        v1.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab_bk.setLayout(v1)
        self.addTab(tab_bk, "Резервное копирование")
        
        tab_st = QWidget()
        v2 = QVBoxLayout()
        self.lbl_stats = QLabel()
        btn_r = QPushButton("Обновить статистику")
        btn_r.clicked.connect(self.load_stats)
        v2.addWidget(self.lbl_stats)
        v2.addWidget(btn_r)
        v2.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab_st.setLayout(v2)
        self.addTab(tab_st, "Системная статистика")
        
        self.load_stats()

    def make_backup(self):
        try:
            create_backup()
            QMessageBox.information(self, "Успех", "Резерваная копия создана")
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к облачному хранилищу")

    def load_stats(self):
        session = SessionLocal()
        cnt = session.query(AppUser).filter(AppUser.is_superuser == False).count()
        self.lbl_stats.setText(f"Всего пользователей: {cnt}")
        session.close()