import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QGroupBox, 
    QHBoxLayout, QLineEdit, QComboBox, QFileDialog, QTabWidget, 
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QSpacerItem, QSizePolicy, QAbstractItemView
)
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

STATUS_EN_TO_RU = {
    "Registration": "Регистрация",
    "Boarding": "Посадка",
    "Departed": "Вылетел",
    "Delayed": "Задержан",
    "Arrived": "Прибыл"
}
STATUS_RU_TO_EN = {v: k for k, v in STATUS_EN_TO_RU.items()}

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
        
        g_air = QGroupBox("Добавить аэропорт")
        f_air = QFormLayout()
        self.air_name = QLineEdit()
        self.air_city_combo = QComboBox()
        self.load_cities()
        f_air.addRow("Название:", self.air_name)
        f_air.addRow("Город:", self.air_city_combo)
        btn_air = QPushButton("Добавить аэропорт")
        btn_air.clicked.connect(self.add_airport)
        v_air = QVBoxLayout()
        v_air.addLayout(f_air)
        v_air.addWidget(btn_air)
        g_air.setLayout(v_air)
        
        vbox.addWidget(g_air)
        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab.setLayout(vbox)
        tabs.addTab(tab, "Инфраструктура")

    def create_fleet_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        g_fleet = QGroupBox("Добавить самолет")
        v_fleet = QVBoxLayout()
        f_fleet = QFormLayout()
        
        self.reg_input = QLineEdit()
        self.type_combo = QComboBox()
        self.load_aircraft_types()
        self.photo_path = None
        
        self.lbl_photo = QLabel("Нет фото")
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_photo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_photo.setStyleSheet("border: 1px dashed #ccc;")
        
        btn_p = QPushButton("Выбрать фото...")
        btn_p.clicked.connect(self.select_photo)
        
        f_fleet.addRow("Рег. номер:", self.reg_input)
        f_fleet.addRow("Модель:", self.type_combo)
        f_fleet.addRow("Фото:", btn_p)
        
        v_fleet.addLayout(f_fleet)
        v_fleet.addWidget(self.lbl_photo)
        
        btn_add = QPushButton("Добавить самолет")
        btn_add.clicked.connect(self.add_aircraft)
        
        v_fleet.addWidget(btn_add)
        g_fleet.setLayout(v_fleet)
        
        vbox.addWidget(g_fleet)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Флот")

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
        self.fl_max.setPlaceholderText("")
        
        self.fl_org = QComboBox()
        self.load_organizations_combo()
        
        form.addRow("Откуда:", self.fl_from)
        form.addRow("Куда:", self.fl_to)
        form.addRow("Время вылета:", self.fl_time)
        form.addRow("Оператор:", self.fl_org)
        form.addRow("Самолет:", self.fl_plane)
        form.addRow("Номер рейса:", self.fl_num)
        form.addRow("Цена:", self.fl_price)
        form.addRow("Мест всего:", self.fl_max)
        
        btn = QPushButton("Создать Рейс")
        btn.clicked.connect(self.create_flight)
        
        vbox.addLayout(form)
        vbox.addWidget(btn)
        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab.setLayout(vbox)
        tabs.addTab(tab, "Расписание")

    def create_manage_flights_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.table_flights = QTableWidget()
        cols = ["Номер", "Откуда", "Куда", "Время вылета", "Самолет", "Цена", "Места", "Статус"]
        self.table_flights.setColumnCount(len(cols))
        self.table_flights.setHorizontalHeaderLabels(cols)
        self.table_flights.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_flights.verticalHeader().setVisible(False)
        self.table_flights.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_flights.setSortingEnabled(True)
        
        btn_ref = QPushButton("Обновить список")
        btn_ref.clicked.connect(self.load_flights_table)
        
        vbox.addWidget(btn_ref)
        vbox.addWidget(self.table_flights)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Управление рейсами")

    def create_flight_report_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.rep_flight_combo = QComboBox()
        self.rep_flight_combo.currentIndexChanged.connect(self.load_flight_passengers)
        
        self.table_pass = QTableWidget()
        self.table_pass.setColumnCount(3)
        self.table_pass.setHorizontalHeaderLabels(["Пассажир", "Паспорт", "Покупатель"])
        self.table_pass.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_pass.verticalHeader().setVisible(False)
        self.table_pass.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        btn_csv = QPushButton("Экспорт в CSV")
        btn_csv.clicked.connect(self.export_passengers)
        
        btn_ref = QPushButton("Обновить список рейсов")
        btn_ref.clicked.connect(self.update_report_combo)

        vbox.addWidget(QLabel("Выберите рейс:"))
        vbox.addWidget(self.rep_flight_combo)
        vbox.addWidget(btn_ref)
        vbox.addWidget(self.table_pass)
        vbox.addWidget(btn_csv)
        tab.setLayout(vbox)
        tabs.addTab(tab, "Список пассажиров")
        self.update_report_combo()

    def create_analytics_tab(self, tabs):
        tab = QWidget()
        vbox = QVBoxLayout()
        
        self.lbl_revenue = QLabel("Нажмите 'Показать выручку'")
        
        btn_show = QPushButton("Показать выручку")
        btn_show.clicked.connect(self.show_analytics)
        
        h = QHBoxLayout()
        btn_csv = QPushButton("Экспорт в CSV")
        btn_csv.clicked.connect(self.export_csv)
        btn_json = QPushButton("Экспорт в JSON")
        btn_json.clicked.connect(self.export_json)
        h.addWidget(btn_csv)
        h.addWidget(btn_json)
        
        vbox.addWidget(self.lbl_revenue)
        vbox.addWidget(btn_show)
        vbox.addLayout(h)
        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab.setLayout(vbox)
        tabs.addTab(tab, "Финансы")

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
            QMessageBox.information(self, "Успех", "Аэропорт добавлен")
            self.load_airports()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Ошибка", "Уже существует")
        finally:
            session.close()

    def load_aircraft_types(self):
        session = SessionLocal()
        self.type_combo.clear()
        for t in session.query(AircraftType).all():
            self.type_combo.addItem(t.model_name, t.id)
        session.close()

    def select_photo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.jpg)")
        if f:
            self.photo_path = f
            self.lbl_photo.setPixmap(QPixmap(f).scaled(self.lbl_photo.size(), Qt.AspectRatioMode.KeepAspectRatio))

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
            QMessageBox.information(self, "Успех", "Самолет добавлен")
            self.load_planes()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Ошибка", "Уже существует")
        finally:
            session.close()

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
        oid = self.fl_org.currentData()
        
        if dep == arr:
            QMessageBox.warning(self, "Ошибка", "Аэропорты должны быть разными")
            return
        
        session = SessionLocal()
        try:
            dt = datetime.strptime(self.fl_time.text(), "%Y-%m-%d %H:%M")
            f = Flight(
                flight_number=num,
                base_price=float(pr),
                max_tickets=int(mx),
                departure_datetime=dt,
                arrival_datetime=dt + timedelta(hours=3),
                departure_airport_id=dep,
                arrival_airport_id=arr,
                aircraft_id=self.fl_plane.currentData(),
                organization_id=oid,
                status="Registration"
            )
            session.add(f)
            session.commit()
            QMessageBox.information(self, "Успех", "Рейс создан")
            self.load_flights_table()
            self.update_report_combo()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты")
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Ошибка", "Номер рейса занят")
        finally:
            session.close()

    def load_flights_table(self):
        self.table_flights.setSortingEnabled(False)
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
            combo.addItems(["Регистрация", "Посадка", "Вылетел", "Задержан", "Прибыл"])
            
            current_status_db = v.status
            current_status_ui = STATUS_EN_TO_RU.get(current_status_db, current_status_db)
            combo.setCurrentText(current_status_ui)
            
            combo.currentTextChanged.connect(lambda text, fid=v.flight_id: self.change_status(fid, text))
            self.table_flights.setCellWidget(i, 7, combo)
        session.close()
        self.table_flights.setSortingEnabled(True)

    def change_status(self, fid, status_ui):
        session = SessionLocal()
        f = session.get(Flight, fid)
        if f:
            status_db = STATUS_RU_TO_EN.get(status_ui, status_ui)
            f.status = status_db
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

    def load_organizations_combo(self):
        session = SessionLocal()
        self.fl_org.clear()
        for org in session.query(Organization).all():
            self.fl_org.addItem(org.organization_name, org.id)
        session.close()

    def export_passengers(self):
        fid = self.rep_flight_combo.currentData()
        if not fid: return
        path = AnalyticsService().export_flight_passengers_csv(fid)
        if path: QMessageBox.information(self, "OK", f"Сохранено: {path}")

    def show_analytics(self):
        s = AnalyticsService().get_airline_revenue_stats()
        text = "\n".join([f"{r[0]}: {r[1]} билетов, ${r[2]}" for r in s]) if s else "Нет данных"
        self.lbl_revenue.setText(text)

    def export_json(self):
        if AnalyticsService().export_stats_json():
            QMessageBox.information(self, "OK", "JSON Сохранен")

    def export_csv(self):
        if AnalyticsService().export_stats_csv():
            QMessageBox.information(self, "OK", "CSV Сохранен")