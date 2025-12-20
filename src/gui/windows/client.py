import uuid
import requests
import bcrypt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QMessageBox, QGroupBox, 
                             QLabel, QComboBox, QLineEdit, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFormLayout)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.exc import IntegrityError
from src.database.db_connection import SessionLocal
from src.database.models.business import Ticket, Flight, Passenger
from src.database.models.auth import AppUser

class ClientWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        self.create_booking_tab(tabs)
        self.create_history_tab(tabs)
        self.create_profile_tab(tabs)
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_booking_tab(self, tabs):
        tab = QWidget()
        v = QVBoxLayout()
        
        self.cl_combo = QComboBox()
        self.cl_combo.currentIndexChanged.connect(self.load_details)
        v.addWidget(QLabel("Select Flight:"))
        v.addWidget(self.cl_combo)
        
        self.lbl_info = QLabel("Details...")
        v.addWidget(self.lbl_info)
        
        self.img = QLabel("No Image")
        self.img.setFixedSize(400, 200)
        self.img.setStyleSheet("border: 1px solid gray;")
        v.addWidget(self.img)
        
        self.p_name = QLineEdit()
        self.p_name.setPlaceholderText("Passenger Name")
        self.p_doc = QLineEdit()
        self.p_doc.setPlaceholderText("Passport")
        v.addWidget(self.p_name)
        v.addWidget(self.p_doc)
        
        self.btn_book = QPushButton("Book")
        self.btn_book.clicked.connect(self.book)
        v.addWidget(self.btn_book)
        
        tab.setLayout(v)
        tabs.addTab(tab, "Search")
        self.load_flights()

    def create_history_tab(self, tabs):
        tab = QWidget()
        v = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Ticket", "Flight", "Passenger"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn = QPushButton("Refresh")
        btn.clicked.connect(self.load_history)
        v.addWidget(btn)
        v.addWidget(self.table)
        
        tab.setLayout(v)
        tabs.addTab(tab, "My Bookings")

    def create_profile_tab(self, tabs):
        tab = QWidget()
        form = QFormLayout()
        
        self.prof_email = QLineEdit()
        self.prof_pass = QLineEdit()
        self.prof_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("New Email:", self.prof_email)
        form.addRow("New Password:", self.prof_pass)
        
        btn = QPushButton("Update Profile")
        btn.clicked.connect(self.update_profile)
        
        w = QWidget()
        l = QVBoxLayout()
        l.addLayout(form)
        l.addWidget(btn)
        w.setLayout(l)
        tabs.addTab(w, "Profile")

    def load_flights(self):
        self.cl_combo.blockSignals(True)
        self.cl_combo.clear()
        session = SessionLocal()
        for f in session.query(Flight).all():
            self.cl_combo.addItem(f"{f.flight_number}", f.id)
        session.close()
        self.cl_combo.blockSignals(False)
        if self.cl_combo.count() > 0: self.load_details()

    def load_details(self):
        fid = self.cl_combo.currentData()
        if not fid: return
        session = SessionLocal()
        try:
            f = session.query(Flight).get(fid)
            self.lbl_info.setText(f"From: {f.departure_airport_id} To: {f.arrival_airport_id}\nPrice: ${f.base_price}")
            self.btn_book.setText(f"Book (${f.base_price})")
            
            if f.aircraft.photo_url:
                try:
                    d = requests.get(f.aircraft.photo_url, timeout=5).content
                    p = QPixmap()
                    p.loadFromData(d)
                    self.img.setPixmap(p.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio))
                except: self.img.setText("Error")
            else: self.img.setText("No Image")
        finally: session.close()

    def book(self):
        fid = self.cl_combo.currentData()
        n = self.p_name.text()
        d = self.p_doc.text()
        if not fid or not n or not d: return
        
        session = SessionLocal()
        try:
            f = session.query(Flight).get(fid)
            p = session.query(Passenger).filter_by(passport_series_number=d).first()
            if not p:
                p = Passenger(first_name=n, last_name=n, passport_series_number=d)
                session.add(p)
                session.flush()
            
            tn = f"T-{str(uuid.uuid4())[:8].upper()}"
            t = Ticket(ticket_number=tn, price=f.base_price, passenger_id=p.id, flight_id=fid, buyer_id=self.user_id)
            session.add(t)
            session.commit()
            QMessageBox.information(self, "Success", "Booked")
            self.load_history()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Already on flight")
        finally: session.close()

    def load_history(self):
        session = SessionLocal()
        ts = session.query(Ticket).filter_by(buyer_id=self.user_id).all()
        self.table.setRowCount(len(ts))
        for i, t in enumerate(ts):
            self.table.setItem(i, 0, QTableWidgetItem(t.ticket_number))
            self.table.setItem(i, 1, QTableWidgetItem(t.flight.flight_number))
            self.table.setItem(i, 2, QTableWidgetItem(t.passenger.last_name))
        session.close()

    def update_profile(self):
        e = self.prof_email.text()
        p = self.prof_pass.text()
        if not e and not p: return
        
        session = SessionLocal()
        try:
            u = session.get(AppUser, self.user_id)
            if e: u.email = e
            if p: u.password_hash = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
            session.commit()
            QMessageBox.information(self, "Success", "Profile updated")
        except:
            session.rollback()
            QMessageBox.warning(self, "Error", "Update failed")
        finally: session.close()