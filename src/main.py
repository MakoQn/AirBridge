import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("AirBridge")
    
    layout = QVBoxLayout()
    label = QLabel("AirBridge")
    layout.addWidget(label)
    window.setLayout(layout)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()