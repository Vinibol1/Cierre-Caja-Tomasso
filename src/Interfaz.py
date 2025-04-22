from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QDateEdit, QFrame, QProgressDialog
)
from PySide6.QtCore import Qt, QDate, QThread, Signal
import MercadoPago
from PySide6.QtGui import QPixmap, QFont
import sys
import Rappi

class WorkerThread(QThread):
    finished = Signal(list)
    progress = Signal(str)
    
    def __init__(self, fecha, driver,etiquetas_totales):
        super().__init__()
        self.fecha = fecha
        self.driver = driver
        self.etiquetas_totales = etiquetas_totales
        self._is_running = True
        
    def run(self):
        try:
            self.progress.emit("Procesando datos...")
            resultados = MercadoPago.ejecutar_programa(self.fecha, self.driver, self.etiquetas_totales)
            if self._is_running:
                self.finished.emit(resultados)
        except Exception as e:
            print(f"Error en WorkerThread: {str(e)}")
            
    def stop(self):
        self._is_running = False

class MainWindow(QWidget):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.worker = None
        self.setup_ui()
        
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
        
    def setup_ui(self):
        self.setWindowTitle("Cierre de caja")
        self.setFixedSize(550, 370)
        self.setStyleSheet("background-color: black;")

        layout_principal = QVBoxLayout(self)

        # Imagen/logo
        imagen_label = QLabel()
        imagen_label.setAlignment(Qt.AlignRight)
        imagen_label.setStyleSheet("background-color: black;")

        # Layouts
        layout_cabecera = QHBoxLayout()
        layout_formulario = QGridLayout()
        layout_botones = QHBoxLayout()

        Nombres = [
            "Total Debito", "Total Credito", "Total Transferencias", "Total Tomasso", "Total fly",
            "Total Rappi Tomasso", "Total Rappi Fly", "Total Fly Turbo","Total Tomasso Turbo"
        ]
        self.etiquetas_totales = []

        fuente = QFont("Helvetica", 15)
        for i, nombre in enumerate(Nombres):
            etiqueta_titulo = QLabel(nombre)
            etiqueta_titulo.setFont(fuente)
            etiqueta_titulo.setStyleSheet("color: white;")
            layout_formulario.addWidget(etiqueta_titulo, i, 0)

            etiqueta_valor = QLabel("0")
            etiqueta_valor.setFont(fuente)
            etiqueta_valor.setStyleSheet("color: white;")
            layout_formulario.addWidget(etiqueta_valor, i, 1)
            self.etiquetas_totales.append(etiqueta_valor)

        # Selector de fecha
        self.fecha_selector = QDateEdit()
        self.fecha_selector.setCalendarPopup(True)
        self.fecha_selector.setDisplayFormat("dd/MM/yyyy")
        self.fecha_selector.setDate(QDate.currentDate())
        self.fecha_selector.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px; border-radius: 4px;")
        layout_botones.addWidget(self.fecha_selector)

        # Botón Confirmar
        boton_confirmar = QPushButton("Confirmar")
        boton_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #14140F;
                color: white;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        boton_confirmar.clicked.connect(self.on_confirmar)
        layout_botones.addWidget(boton_confirmar)

        boton_salir = QPushButton("Salir")
        boton_salir.setStyleSheet("""
            QPushButton {
                background-color: #600000;
                color: white;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #800000;
            }
        """)
        boton_salir.clicked.connect(QApplication.instance().quit)
        layout_botones.addWidget(boton_salir)

        layout_cabecera.addStretch()
        layout_cabecera.addWidget(imagen_label)

        layout_principal.addLayout(layout_formulario)
        layout_principal.addSpacing(10)
        layout_principal.addLayout(layout_botones)
        layout_principal.addLayout(layout_cabecera)

        self.setLayout(layout_principal)
        
    def on_confirmar(self):
        if self.worker and self.worker.isRunning():
            return
            
        progress = QProgressDialog("Procesando...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setWindowTitle("Por favor espere")
        progress.show()

        self.worker = WorkerThread(self.fecha_selector, self.driver,self.etiquetas_totales)
        self.worker.finished.connect(lambda results: self.actualizar_interfaz(results))
        self.worker.finished.connect(progress.close)
        self.worker.start()

    def actualizar_interfaz(self, resultados):
        for i in range(9):
            self.etiquetas_totales[i].setText(str(resultados[i]))

def interfaz(driver):
    app = QApplication(sys.argv)
    window = MainWindow(driver)
    window.show()
    sys.exit(app.exec())