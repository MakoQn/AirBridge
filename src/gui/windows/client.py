import uuid
import requests
import bcrypt
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QGroupBox,
    QLabel, QComboBox, QLineEdit, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFormLayout, QHBoxLayout, QDateEdit,
    QAbstractItemView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate
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
        
        self.create_search_tab(tabs)
        self.create_history_tab(tabs)
        self.create_profile_tab(tabs)
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_search_tab(self, tabs):
        tab = QWidget()
        v = QVBoxLayout()
        
        h_filter = QHBoxLayout()
        self.filter_from = QLineEdit()
        self.filter_from.setPlaceholderText("Откуда")
        self.filter_to = QLineEdit()
        self.filter_to.setPlaceholderText("Куда")
        self.filter_date = QDateEdit()
        self.filter_date.setDate(QDate.currentDate())
        btn_search = QPushButton("Найти")
        btn_search.clicked.connect(self.search_flights)
        h_filter.addWidget(self.filter_from)
        h_filter.addWidget(self.filter_to)
        h_filter.addWidget(self.filter_date)
        h_filter.addWidget(btn_search)
        v.addLayout(h_filter)
        
        self.cl_combo = QComboBox()
        self.cl_combo.currentIndexChanged.connect(self.load_details)
        v.addWidget(QLabel("Доступные рейсы:"))
        v.addWidget(self.cl_combo)
        
        g_det = QGroupBox("Подробности")
        f_det = QFormLayout()
        self.lbl_num = QLabel()
        self.lbl_org = QLabel()
        self.lbl_route = QLabel()
        self.lbl_time = QLabel()
        self.lbl_plane = QLabel()
        self.lbl_seats = QLabel()
        self.lbl_price = QLabel()
        self.img = QLabel("Нет фото")
        self.img.setFixedSize(300, 200)
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        f_det.addRow("Рейс:", self.lbl_num)
        f_det.addRow("Авиакомпания:", self.lbl_org)
        f_det.addRow("Маршрут:", self.lbl_route)
        f_det.addRow("Время:", self.lbl_time)
        f_det.addRow("Самолет:", self.lbl_plane)
        f_det.addRow("Мест:", self.lbl_seats)
        f_det.addRow("Цена:", self.lbl_price)
        f_det.addRow("Фото:", self.img)
        g_det.setLayout(f_det)
        v.addWidget(g_det)
        
        self.p_last = QLineEdit()
        self.p_last.setPlaceholderText("Фамилия")
        self.p_first = QLineEdit()
        self.p_first.setPlaceholderText("Имя")
        self.p_middle = QLineEdit()
        self.p_middle.setPlaceholderText("Отчество (необязательно)")
        self.p_doc = QLineEdit()
        self.p_doc.setPlaceholderText("Номер паспорта")
        
        v.addWidget(self.p_last)
        v.addWidget(self.p_first)
        v.addWidget(self.p_middle)
        v.addWidget(self.p_doc)
        
        btn_book = QPushButton("Купить билет")
        btn_book.clicked.connect(self.book)
        v.addWidget(btn_book)
        
        tab.setLayout(v)
        tabs.addTab(tab, "Поиск рейсов")
        self.search_flights()

    def create_history_tab(self, tabs):
        tab = QWidget()
        v = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Рейс", "Маршрут", "Время", "Пассажир"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        btn = QPushButton("Обновить")
        btn.clicked.connect(self.load_history)
        v.addWidget(btn)
        v.addWidget(self.table)
        
        tab.setLayout(v)
        tabs.addTab(tab, "Мои бронирования")

    def create_profile_tab(self, tabs):
        tab = QWidget()
        form = QFormLayout()
        
        self.prof_user = QLineEdit()
        self.prof_email = QLineEdit()
        self.prof_pass = QLineEdit()
        self.prof_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("Новое имя пользователя:", self.prof_user)
        form.addRow("Новый Email:", self.prof_email)
        form.addRow("Новый пароль:", self.prof_pass)
        
        btn = QPushButton("Обновить профиль")
        btn.clicked.connect(self.update_profile)
        
        w = QWidget()
        l = QVBoxLayout()
        l.addLayout(form)
        l.addWidget(btn)
        w.setLayout(l)
        tabs.addTab(w, "Профиль")

    def search_flights(self):
        self.cl_combo.blockSignals(True)
        self.cl_combo.clear()
        
        city_from = self.filter_from.text().lower()
        city_to = self.filter_to.text().lower()
        
        session = SessionLocal()
        try:
            query = session.query(Flight).filter(Flight.status == "Registration")
            flights = query.all()
            for f in flights:
                dep_city = f.departure_airport.city.city_name.lower()
                arr_city = f.arrival_airport.city.city_name.lower()
                
                if city_from and city_from not in dep_city: continue
                if city_to and city_to not in arr_city: continue
                
                self.cl_combo.addItem(f"{f.flight_number} ({f.departure_airport.city.city_name} -> {f.arrival_airport.city.city_name})", f.id)
        finally:
            session.close()
            self.cl_combo.blockSignals(False)
        
        if self.cl_combo.count() > 0: self.load_details()
        else: self.clear_details()

    def clear_details(self):
        self.lbl_num.setText("-")
        self.lbl_seats.setText("-")
        self.img.setText("Нет рейсов")

    def load_details(self):
        fid = self.cl_combo.currentData()
        if not fid: 
            self.img.setText("Рейс не выбран")
            return
        
        session = SessionLocal()
        try:
            f = session.query(Flight).get(fid)
            seats_sold = len(f.tickets)
            seats_left = f.max_tickets - seats_sold
            
            self.lbl_num.setText(f.flight_number)
            self.lbl_org.setText(f.organization.organization_name)
            self.lbl_route.setText(f"{f.departure_airport.city.city_name} -> {f.arrival_airport.city.city_name}")
            self.lbl_time.setText(str(f.departure_datetime))
            self.lbl_plane.setText(f"{f.aircraft.aircraft_type.model_name} ({f.aircraft.registration_number})")
            self.lbl_seats.setText(str(seats_left))
            self.lbl_price.setText(str(f.base_price))
            
            if f.aircraft.photo_url:
                try:
                    d = requests.get(f.aircraft.photo_url, timeout=3).content
                    p = QPixmap()
                    p.loadFromData(d)
                    self.img.setPixmap(p.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))
                except: 
                    self.img.setText("Ошибка загрузки фото")
            else: 
                self.img.setText("Нет фото")
        finally:
            session.close()

    def book(self):
        fid = self.cl_combo.currentData()
        lname = self.p_last.text().strip()
        fname = self.p_first.text().strip()
        mname = self.p_middle.text().strip()
        doc = self.p_doc.text().strip()
        
        if not fid or not lname or not fname or not doc:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
            return
        
        session = SessionLocal()
        try:
            f = session.query(Flight).get(fid)
            if len(f.tickets) >= f.max_tickets:
                QMessageBox.warning(self, "Ошибка", "Мест нет!")
                return

            p = session.query(Passenger).filter_by(passport_series_number=doc).first()
            if not p:
                p = Passenger(
                    first_name=fname,
                    last_name=lname,
                    middle_name=mname,
                    passport_series_number=doc
                )
                session.add(p)
                session.flush()
            
            tn = f"T-{uuid.uuid4().hex[:8].upper()}"
            t = Ticket(ticket_number=tn, price=f.base_price, passenger_id=p.id, flight_id=fid, buyer_id=self.user_id)
            session.add(t)
            session.commit()
            QMessageBox.information(self, "Успех", "Билет куплен!")
            self.load_history()
            self.load_details()
        except IntegrityError:
            session.rollback()
            QMessageBox.warning(self, "Ошибка", "Пассажир уже зарегистрирован на рейс")
        finally: session.close()

    def load_history(self):
        session = SessionLocal()
        ts = session.query(Ticket).filter_by(buyer_id=self.user_id).all()
        self.table.setRowCount(len(ts))
        for i, t in enumerate(ts):
            it_fl = QTableWidgetItem(t.ticket_number)
            it_fl.setFlags(it_fl.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, it_fl)
            
            route = f"{t.flight.departure_airport.city.city_name} -> {t.flight.arrival_airport.city.city_name}"
            it_rt = QTableWidgetItem(route)
            it_rt.setFlags(it_rt.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, it_rt)
            
            it_tm = QTableWidgetItem(str(t.flight.departure_datetime))
            it_tm.setFlags(it_tm.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, it_tm)
            
            full_name = f"{t.passenger.last_name} {t.passenger.first_name}"
            if t.passenger.middle_name:
                full_name += f" {t.passenger.middle_name}"
                
            it_ps = QTableWidgetItem(full_name)
            it_ps.setFlags(it_ps.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, it_ps)
        session.close()

    def update_profile(self):
        u_name = self.prof_user.text()
        e = self.prof_email.text()
        p = self.prof_pass.text()
        
        session = SessionLocal()
        try:
            u = session.get(AppUser, self.user_id)
            changed = False
            
            if u_name and u.username != u_name:
                if session.query(AppUser).filter(AppUser.username == u_name, AppUser.id != self.user_id).first():
                    QMessageBox.warning(self, "Ошибка", "Имя пользователя занято")
                    return
                u.username = u_name
                changed = True
            
            if e and u.email != e:
                if session.query(AppUser).filter(AppUser.email == e, AppUser.id != self.user_id).first():
                    QMessageBox.warning(self, "Ошибка", "Email занят")
                    return
                u.email = e
                changed = True
                
            if p:
                u.password_hash = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
                changed = True
            
            if changed:
                session.commit()
                QMessageBox.information(self, "Успех", "Профиль обновлен")
            else:
                QMessageBox.information(self, "Информация", "Нет изменений")
                
        except Exception as err:
            session.rollback()
            QMessageBox.warning(self, "Ошибка", str(err))
        finally: session.close()