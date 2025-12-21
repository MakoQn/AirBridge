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
from src.database.models.reports import FlightDetailsView

class DispatcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        self.create_infra_tab(tabs)
        self.create_fleet_tab(tabs)
        self.create_schedule_tab(tabs)
        self.create_manage_flights_tab(tabs)
        self.create_flight_report_tab(tabs)
        self.create_analytics_tab(tabs)
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_infra_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        g_air = QGroupBox("Add Airport")
        f_air = QFormLayout()
        self.air_name = QLineEdit()
        self.air_city_combo = QComboBox()
        self.load_cities()
        f_air.addRow("Name:", self.air_name)
        f_air.addRow("City:", self.air_city_combo)
        btn_air = QPushButton("Add Airport")
        btn_air.clicked.connect(self.add_airport)
        v_air = QVBoxLayout()
        v_air.addLayout(f_air)
        v_air.addWidget(btn_air)
        g_air.setLayout(v_air)
        
        vbox.addWidget(g_air)
        tab.setLayout(vbox)
        tabs.addTab(tab, "1. Infrastructure")

    def create_fleet_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        g_fleet = QGroupBox("Add Aircraft")
        f_fleet = QFormLayout()
        self.reg_input = QLineEdit()
        self.type_combo = QComboBox()
        self.load_aircraft_types()
        self.photo_path = None
        self.lbl_photo = QLabel("No photo")
        self.lbl_photo.setFixedSize(100, 70)
        self.lbl_photo.setStyleSheet("border: 1px solid #ccc;")
        btn_p = QPushButton("Select Photo")
        btn_p.clicked.connect(self.select_photo)
        f_fleet.addRow("Reg. Number:", self.reg_input)
        f_fleet.addRow("Model:", self.type_combo)
        f_fleet.addRow("Photo:", btn_p)
        f_fleet.addRow("", self.lbl_photo)
        btn_fleet = QPushButton("Add Aircraft")
        btn_fleet.clicked.connect(self.add_aircraft)
        v_fleet = QVBoxLayout()
        v_fleet.addLayout(f_fleet)
        v_fleet.addWidget(btn_fleet)
        g_fleet.setLayout(v_fleet)
        
        vbox.addWidget(g_fleet)
        tab.setLayout(vbox)
        tabs.addTab(tab, "2. Fleet")

    def create_schedule_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        form = QFormLayout()
        
        self.fl_from = QComboBox()
        self.fl_to = QComboBox()
        self.load_airports()
        
        self.fl_time = QLineEdit()
        self.fl_time.setPlaceholderText("YYYY-MM-DD HH:MM")
        self.fl_time.setText((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
        
        self.fl_plane = QComboBox()
        self.load_planes()
        
        self.fl_num = QLineEdit()
        self.fl_price = QLineEdit()
        self.fl_max = QLineEdit()
        self.fl_max.setPlaceholderText("100")
        
        form.addRow("From:", self.fl_from)
        form.addRow("To:", self.fl_to)
        form.addRow("Time:", self.fl_time)
        form.addRow("Aircraft:", self.fl_plane)
        form.addRow("Flight Number:", self.fl_num)
        form.addRow("Price:", self.fl_price)
        form.addRow("Max Seats:", self.fl_max)
        
        btn = QPushButton("Create Flight")
        btn.clicked.connect(self.create_flight)
        
        vbox.addLayout(form)
        vbox.addWidget(btn)
        tab.setLayout(vbox)
        tabs.addTab(tab, "3. Schedule")

    def create_manage_flights_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.table_flights = QTableWidget()
        cols = ["Number", "From", "To", "Time", "Plane", "Price", "Sold", "Status"]
        self.table_flights.setColumnCount(len(cols))
        self.table_flights.setHorizontalHeaderLabels(cols)
        self.table_flights.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn_ref = QPushButton("Refresh List")
        btn_ref.clicked.connect(self.load_flights_table)
        
        vbox.addWidget(btn_ref)
        vbox.addWidget(self.table_flights)
        tab.setLayout(vbox)
        tabs.addTab(tab, "4. Flight Control")

    def create_flight_report_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.rep_flight_combo = QComboBox()
        self.rep_flight_combo.currentIndexChanged.connect(self.load_flight_passengers)
        
        self.table_pass = QTableWidget()
        self.table_pass.setColumnCount(3)
        self.table_pass.setHorizontalHeaderLabels(["Passenger Name", "Passport", "Buyer (Account)"])
        self.table_pass.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn_csv = QPushButton("Export to CSV")
        btn_csv.clicked.connect(self.export_passengers)
        
        btn_ref = QPushButton("Refresh Flights List")
        btn_ref.clicked.connect(self.update_report_combo)

        vbox.addWidget(QLabel("Select Flight:"))
        vbox.addWidget(self.rep_flight_combo)
        vbox.addWidget(btn_ref)
        vbox.addWidget(self.table_pass)
        vbox.addWidget(btn_csv)
        tab.setLayout(vbox)
        tabs.addTab(tab, "5. Passenger Lists")
        self.update_report_combo()

    def create_analytics_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.lbl_revenue = QLabel("Click Show to see data")
        
        btn_show = QPushButton("Show Revenue")
        btn_show.clicked.connect(self.show_analytics)
        
        h = QHBoxLayout()
        btn_csv = QPushButton("Export Revenue CSV")
        btn_csv.clicked.connect(self.export_csv)
        btn_json = QPushButton("Export Revenue JSON")
        btn_json.clicked.connect(self.export_json)
        h.addWidget(btn_csv)
        h.addWidget(btn_json)
        
        vbox.addWidget(self.lbl_revenue)
        vbox.addWidget(btn_show)
        vbox.addLayout(h)
        tab.setLayout(vbox)
        tabs.addTab(tab, "6. Finance")

    def load_cities(self):
        session = SessionLocal()
        self.air_city_combo.clear()
        for c in session.query(City).all():
            self.air_city_combo.addItem(c.city_name, c.id)
        session.close()

    def add_airport(self):
        name = self.air_name.text()
        if not name: return
        session = SessionLocal()
        try:
            session.add(Airport(airport_name=name, city_id=self.air_city_combo.currentData()))
            session.commit()
            QMessageBox.information(self, "Success", "Added")
            self.load_airports()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Already exists")
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
            self.lbl_photo.setPixmap(QPixmap(f).scaled(100, 70))

    def add_aircraft(self):
        reg = self.reg_input.text()
        if not reg: return
        url = None
        if self.photo_path:
            try:
                url = MinioService().upload_file(self.photo_path, f"aircrafts/{os.path.basename(self.photo_path)}")
            except: pass
        session = SessionLocal()
        try:
            session.add(Aircraft(registration_number=reg, aircraft_type_id=self.type_combo.currentData(), photo_url=url))
            session.commit()
            QMessageBox.information(self, "Success", "Added")
            self.load_planes()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Exists")
        finally: session.close()

    def load_airports(self):
        session = SessionLocal()
        self.fl_from.clear()
        self.fl_to.clear()
        for a in session.query(Airport).all():
            t = f"{a.airport_name} ({a.city.city_name})"
            self.fl_from.addItem(t, a.id)
            self.fl_to.addItem(t, a.id)
        session.close()

    def load_planes(self):
        session = SessionLocal()
        self.fl_plane.clear()
        for p in session.query(Aircraft).all():
            self.fl_plane.addItem(p.registration_number, p.id)
        session.close()

    def create_flight(self):
        num = self.fl_num.text()
        pr = self.fl_price.text()
        mx = self.fl_max.text()
        dep = self.fl_from.currentData()
        arr = self.fl_to.currentData()
        
        if dep == arr:
            QMessageBox.warning(self, "Error", "Same airports")
            return
        
        session = SessionLocal()
        try:
            dt = datetime.strptime(self.fl_time.text(), "%Y-%m-%d %H:%M")
            org = session.query(Organization).first()
            f = Flight(
                flight_number=num,
                base_price=float(pr),
                max_tickets=int(mx),
                departure_datetime=dt,
                arrival_datetime=dt + timedelta(hours=3),
                departure_airport_id=dep,
                arrival_airport_id=arr,
                aircraft_id=self.fl_plane.currentData(),
                organization_id=org.id,
                status="Registration"
            )
            session.add(f)
            session.commit()
            QMessageBox.information(self, "Success", "Flight Created")
            self.load_flights_table()
            self.update_report_combo()
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid date format")
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Error", "Flight number exists")
        finally: session.close()

    def load_flights_table(self):
        session = SessionLocal()
        views = session.query(FlightDetailsView).all()
        
        self.table_flights.setRowCount(len(views))
        for i, v in enumerate(views):
            sold = session.query(Ticket).filter(Ticket.flight_id == v.flight_id).count()
            
            item_num = QTableWidgetItem(v.flight_number)
            item_num.setFlags(item_num.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 0, item_num)
            
            item_dep = QTableWidgetItem(v.dep_city)
            item_dep.setFlags(item_dep.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 1, item_dep)

            item_arr = QTableWidgetItem(v.arr_city)
            item_arr.setFlags(item_arr.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 2, item_arr)

            item_time = QTableWidgetItem(str(v.departure_datetime))
            item_time.setFlags(item_time.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 3, item_time)

            item_plane = QTableWidgetItem(v.aircraft_reg)
            item_plane.setFlags(item_plane.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 4, item_plane)

            item_price = QTableWidgetItem(str(v.base_price))
            item_price.setFlags(item_price.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 5, item_price)

            item_sold = QTableWidgetItem(f"{sold}/{v.max_tickets}")
            item_sold.setFlags(item_sold.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_flights.setItem(i, 6, item_sold)
            
            combo = QComboBox()
            combo.addItems(["Registration", "Boarding", "Departed", "Delayed", "Arrived"])
            combo.setCurrentText(v.status)
            combo.currentTextChanged.connect(lambda text, fid=v.flight_id: self.change_status(fid, text))
            self.table_flights.setCellWidget(i, 7, combo)
        session.close()

    def change_status(self, fid, status):
        session = SessionLocal()
        f = session.get(Flight, fid)
        if f:
            f.status = status
            session.commit()
        session.close()

    def update_report_combo(self):
        session = SessionLocal()
        self.rep_flight_combo.clear()
        for f in session.query(Flight).all():
            self.rep_flight_combo.addItem(f.flight_number, f.id)
        session.close()

    def load_flight_passengers(self):
        fid = self.rep_flight_combo.currentData()
        if not fid: return
        session = SessionLocal()
        tickets = session.query(Ticket).filter_by(flight_id=fid).all()
        self.table_pass.setRowCount(len(tickets))
        for i, t in enumerate(tickets):
            buyer = t.buyer.username if t.buyer else "N/A"
            
            it_name = QTableWidgetItem(f"{t.passenger.last_name} {t.passenger.first_name}")
            it_name.setFlags(it_name.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_pass.setItem(i, 0, it_name)
            
            it_doc = QTableWidgetItem(t.passenger.passport_series_number)
            it_doc.setFlags(it_doc.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_pass.setItem(i, 1, it_doc)
            
            it_buy = QTableWidgetItem(buyer)
            it_buy.setFlags(it_buy.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_pass.setItem(i, 2, it_buy)
        session.close()

    def export_passengers(self):
        fid = self.rep_flight_combo.currentData()
        if not fid: return
        path = AnalyticsService().export_flight_passengers_csv(fid)
        if path: QMessageBox.information(self, "OK", f"Saved to {path}")

    def show_analytics(self):
        s = AnalyticsService().get_airline_revenue_stats()
        text = "\n".join([f"{r[0]}: {r[1]} tkt, ${r[2]}" for r in s]) if s else "No data"
        self.lbl_revenue.setText(text)

    def export_json(self):
        if AnalyticsService().export_stats_json(): QMessageBox.information(self, "OK", "JSON Saved")

    def export_csv(self):
        if AnalyticsService().export_stats_csv(): QMessageBox.information(self, "OK", "CSV Saved")