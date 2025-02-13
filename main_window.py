from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QSizePolicy, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from omr_gui import OMRApp
from template_download import TemplateDownloadScreen
from instructions import InstructionsScreen
from report_screen import ReportScreen  # Импортируем экран отчета

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сканер тестов")
        # Основной виджет и макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        # Стек виджетов для разных экранов
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        # Стилизация главного окна и всех экранов
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
                color: #D8DEE9;
            }
            QWidget#central_widget, QWidget#main_menu, QWidget#omr_screen, QWidget#template_download_screen, QWidget#instructions_screen, QWidget#report_screen {
                background-color: #3B4252;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #D8DEE9;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        # Главное меню
        self.main_menu = QWidget()
        self.main_menu.setObjectName("main_menu")
        self.main_menu_layout = QVBoxLayout(self.main_menu)
        self.main_menu_layout.setAlignment(Qt.AlignCenter)
        # Анимированная надпись "Сканер тестов"
        self.title_label = QLabel("Сканер тестов")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #88C0D0;")
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(10)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setColor(Qt.white)  # Белый контур
        self.title_label.setGraphicsEffect(shadow_effect)
        self.main_menu_layout.addWidget(self.title_label)
        # Создание анимации для изменения прозрачности
        self.animation = QPropertyAnimation(self.title_label, b"windowOpacity")
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setLoopCount(-1)  # Зацикливаем анимацию
        self.animation.start()
        # Кнопка "Начать проверку"
        self.start_check_button = QPushButton("Начать проверку")
        self.start_check_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.start_check_button.clicked.connect(self.show_omr_screen)
        self.main_menu_layout.addWidget(self.start_check_button, alignment=Qt.AlignCenter)
        # Кнопка "Скачать шаблон бланка"
        self.download_template_button = QPushButton("Скачать шаблон бланка")
        self.download_template_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.download_template_button.clicked.connect(self.show_template_download_screen)
        self.main_menu_layout.addWidget(self.download_template_button, alignment=Qt.AlignCenter)
        # Кнопка "Инструкция"
        self.instructions_button = QPushButton("Инструкция")
        self.instructions_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.instructions_button.clicked.connect(self.show_instructions_screen)
        self.main_menu_layout.addWidget(self.instructions_button, alignment=Qt.AlignCenter)
        # Кнопка "Отчет" (новая кнопка)
        self.report_button = QPushButton("Отчет")
        self.report_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.report_button.clicked.connect(self.show_report_screen)
        self.main_menu_layout.addWidget(self.report_button, alignment=Qt.AlignCenter)
        # Кнопка "Выход"
        self.exit_button = QPushButton("Выход")
        self.exit_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.exit_button.clicked.connect(self.close)
        self.main_menu_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)
        # Добавление главного меню в стек виджетов
        self.stacked_widget.addWidget(self.main_menu)
        # Инициализация экранов и добавление их в стек виджетов
        self.omr_screen = OMRApp(self)
        self.omr_screen.setObjectName("omr_screen")
        self.stacked_widget.addWidget(self.omr_screen)
        # Экран "Скачать шаблон бланка"
        self.template_download_screen = TemplateDownloadScreen(self)
        self.template_download_screen.setObjectName("template_download_screen")
        self.stacked_widget.addWidget(self.template_download_screen)
        # Экран "Инструкция"
        self.instructions_screen = InstructionsScreen(self)
        self.instructions_screen.setObjectName("instructions_screen")
        self.stacked_widget.addWidget(self.instructions_screen)
        # Экран "Отчет" (новый экран)
        self.report_screen = ReportScreen(self)
        self.report_screen.setObjectName("report_screen")
        self.stacked_widget.addWidget(self.report_screen)
        # Маленькая надпись для брендинга "МБОУ СОШ №14"
        self.branding_label = QLabel("МБОУ СОШ №14")
        branding_font = QFont("Arial", 10, QFont.Bold)  # Меньший шрифт для брендинга
        self.branding_label.setFont(branding_font)
        self.branding_label.setStyleSheet("color: #ECEFF4;")
        branding_shadow_effect = QGraphicsDropShadowEffect(self)
        branding_shadow_effect.setBlurRadius(10)
        branding_shadow_effect.setColor(Qt.white)  # Белый контур
        branding_shadow_effect.setOffset(0, 0)
        self.branding_label.setGraphicsEffect(branding_shadow_effect)
        self.layout.addWidget(self.branding_label, alignment=Qt.AlignBottom | Qt.AlignRight)
        # Показ главного меню
        self.stacked_widget.setCurrentWidget(self.main_menu)

    # Методы для перехода между экранами
    def show_omr_screen(self):
        self.omr_screen.start_camera()
        self.stacked_widget.setCurrentWidget(self.omr_screen)

    def show_template_download_screen(self):
        self.stacked_widget.setCurrentWidget(self.template_download_screen)

    def show_instructions_screen(self):
        self.stacked_widget.setCurrentWidget(self.instructions_screen)

    def show_report_screen(self):
        self.stacked_widget.setCurrentWidget(self.report_screen)

    def show_main_menu(self):
        self.omr_screen.stop_camera()
        self.stacked_widget.setCurrentWidget(self.main_menu)