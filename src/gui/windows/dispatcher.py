import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QMessageBox, QGroupBox, 
                             QHBoxLayout, QLineEdit, QComboBox, QFileDialog, QTabWidget, 
                             QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.exc import IntegrityError
from src.services.analytics_service import AnalyticsService
from src.services.minio_service import MinioService
from src.database.db_connection import SessionLocal
from src.database.models.fleet import Aircraft, AircraftType
from src.database.models.business import Ticket, Flight, Organization
from src.database.models.geo import Airport, City

class DispatcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        self.create_infra_tab(tabs)
        self.create_fleet_tab(tabs)
        self.create_schedule_tab(tabs)
        self.create_bookings_tab(tabs)
        self.create_analytics_tab(tabs)
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_infra_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        form = QFormLayout()
        
        self.air_name = QLineEdit()
        self.air_city_combo = QComboBox()
        self.load_cities()
        
        form.addRow("Airport Name:", self.air_name)
        form.addRow("City:", self.air_city_combo)
        
        btn = QPushButton("Add Airport")
        btn.clicked.connect(self.add_airport)
        vbox.addLayout(form)
        vbox.addWidget(btn)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Infrastructure")

    def create_fleet_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        form = QFormLayout()
        
        self.reg_input = QLineEdit()
        self.type_combo = QComboBox()
        self.load_aircraft_types()
        self.photo_path = None
        
        self.lbl_photo = QLabel("No photo")
        self.lbl_photo.setFixedSize(150, 100)
        self.lbl_photo.setStyleSheet("border: 1px solid #ccc;")
        
        btn_p = QPushButton("Select Photo...")
        btn_p.clicked.connect(self.select_photo)
        
        form.addRow("Registration:", self.reg_input)
        form.addRow("Type:", self.type_combo)
        form.addRow("Photo:", btn_p)
        form.addRow("", self.lbl_photo)
        
        btn_add = QPushButton("Add Aircraft")
        btn_add.clicked.connect(self.add_aircraft)
        vbox.addLayout(form)
        vbox.addWidget(btn_add)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Fleet")

    def create_schedule_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        form = QFormLayout()
        
        self.fl_number = QLineEdit()
        self.fl_price = QLineEdit()
        self.fl_plane_combo = QComboBox()
        self.fl_dep_combo = QComboBox()
        self.fl_arr_combo = QComboBox()
        self.fl_org_combo = QComboBox()
        self.load_flight_data()
        
        form.addRow("Flight #:", self.fl_number)
        form.addRow("Price ($):", self.fl_price)
        form.addRow("Operator:", self.fl_org_combo)
        form.addRow("Aircraft:", self.fl_plane_combo)
        form.addRow("From:", self.fl_dep_combo)
        form.addRow("To:", self.fl_arr_combo)
        
        btn = QPushButton("Create Flight")
        btn.clicked.connect(self.create_flight)
        vbox.addLayout(form)
        vbox.addWidget(btn)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Schedule")

    def create_bookings_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.table_bk = QTableWidget()
        self.table_bk.setColumnCount(5)
        self.table_bk.setHorizontalHeaderLabels(["Ticket", "Flight", "Passenger", "Buyer", "Price"])
        self.table_bk.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        h = QHBoxLayout()
        btn_ref = QPushButton("Refresh")
        btn_ref.clicked.connect(self.load_bookings)
        btn_exp = QPushButton("Export CSV")
        btn_exp.clicked.connect(self.export_bookings)
        h.addWidget(btn_ref)
        h.addWidget(btn_exp)
        
        vbox.addLayout(h)
        vbox.addWidget(self.table_bk)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Bookings")

    def create_analytics_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        btn_show = QPushButton("Show Revenue")
        btn_show.clicked.connect(self.show_analytics)
        
        h = QHBoxLayout()
        btn_csv = QPushButton("Export CSV")
        btn_csv.clicked.connect(self.export_csv)
        btn_json = QPushButton("Export JSON")
        btn_json.clicked.connect(self.export_json)
        h.addWidget(btn_csv)
        h.addWidget(btn_json)
        
        vbox.addWidget(btn_show)
        vbox.addLayout(h)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Analytics")

    def load_cities(self):
        session = SessionLocal()
        self.air_city_combo.clear()
        for c in session.query(City).all():
            self.air_city_combo.addItem(c.city_name, c.id)
        session.close()

    def add_airport(self):
        name = self.air_name.text()
        cid = self.air_city_combo.currentData()
        if not name: return
        session = SessionLocal()
        try:
            session.add(Airport(airport_name=name, city_id=cid))
            session.commit()
            QMessageBox.information(self, "Success", "Added")
            self.load_flight_data()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Exists")
        finally: session.close()

    def load_aircraft_types(self):
        session = SessionLocal()
        self.type_combo.clear()
        for t in session.query(AircraftType).all():
            self.type_combo.addItem(t.model_name, t.id)
        session.close()

    def select_photo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Image", "", "Images (*.png *.jpg)")
        if f:
            self.photo_path = f
            self.lbl_photo.setPixmap(QPixmap(f).scaled(150, 100))

    def add_aircraft(self):
        reg = self.reg_input.text()
        tid = self.type_combo.currentData()
        if not reg: return
        url = None
        if self.photo_path:
            try:
                url = MinioService().upload_file(self.photo_path, f"aircrafts/{os.path.basename(self.photo_path)}")
            except: pass
        session = SessionLocal()
        try:
            session.add(Aircraft(registration_number=reg, aircraft_type_id=tid, photo_url=url))
            session.commit()
            QMessageBox.information(self, "Success", "Added")
            self.load_flight_data()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Exists")
        finally: session.close()

    def load_flight_data(self):
        session = SessionLocal()
        self.fl_plane_combo.clear()
        self.fl_dep_combo.clear()
        self.fl_arr_combo.clear()
        self.fl_org_combo.clear()
        for p in session.query(Aircraft).all():
            self.fl_plane_combo.addItem(p.registration_number, p.id)
        for a in session.query(Airport).all():
            t = f"{a.airport_name} ({a.city.city_name})"
            self.fl_dep_combo.addItem(t, a.id)
            self.fl_arr_combo.addItem(t, a.id)
        for o in session.query(Organization).all():
            self.fl_org_combo.addItem(o.organization_name, o.id)
        session.close()

    def create_flight(self):
        num = self.fl_number.text()
        pr = self.fl_price.text()
        pid = self.fl_plane_combo.currentData()
        did = self.fl_dep_combo.currentData()
        aid = self.fl_arr_combo.currentData()
        oid = self.fl_org_combo.currentData()
        if not num or not pr or did == aid: return
        session = SessionLocal()
        try:
            f = Flight(flight_number=num, base_price=float(pr),
                       departure_datetime=datetime.now()+timedelta(days=1),
                       arrival_datetime=datetime.now()+timedelta(days=1, hours=2),
                       departure_airport_id=did, arrival_airport_id=aid,
                       organization_id=oid, aircraft_id=pid)
            session.add(f)
            session.commit()
            QMessageBox.information(self, "Success", "Created")
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Exists")
        finally: session.close()

    def load_bookings(self):
        session = SessionLocal()
        try:
            ts = session.query(Ticket).all()
            self.table_bk.setRowCount(len(ts))
            for i, t in enumerate(ts):
                bn = t.buyer.username if t.buyer else "N/A"
                self.table_bk.setItem(i, 0, QTableWidgetItem(t.ticket_number))
                self.table_bk.setItem(i, 1, QTableWidgetItem(t.flight.flight_number))
                self.table_bk.setItem(i, 2, QTableWidgetItem(f"{t.passenger.last_name}"))
                self.table_bk.setItem(i, 3, QTableWidgetItem(bn))
                self.table_bk.setItem(i, 4, QTableWidgetItem(str(t.price)))
        finally: session.close()

    def export_bookings(self):
        if AnalyticsService().export_bookings_csv():
            QMessageBox.information(self, "OK", "Exported")

    def show_analytics(self):
        s = AnalyticsService().get_airline_revenue_stats()
        t = "\n".join([f"{r[0]}: {r[1]} tkt, ${r[2]}" for r in s]) if s else "No data"
        QMessageBox.information(self, "Analytics", t)

    def export_csv(self):
        if AnalyticsService().export_stats_csv(): QMessageBox.information(self, "OK", "Saved")

    def export_json(self):
        if AnalyticsService().export_stats_json(): QMessageBox.information(self, "OK", "Saved")