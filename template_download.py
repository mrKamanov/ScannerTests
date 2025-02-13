import os
import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt

class TemplateDownloadScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        # Установка стилей для экрана
        self.setStyleSheet("""
            QWidget {
                background-color: #3B4252;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #D8DEE9;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        # Кнопка "Назад"
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        # Текстовая метка
        self.label = QLabel("Скачайте шаблон бланка и шрифт.Если вы получили ошибку, то проверьте папку с программой")
        self.layout.addWidget(self.label)
        # Кнопка для скачивания шаблона
        self.download_template_button = QPushButton("Скачать шаблон бланка")
        self.download_template_button.clicked.connect(self.download_template)
        self.layout.addWidget(self.download_template_button)
        # Кнопка для скачивания шрифта
        self.download_font_button = QPushButton("Скачать шрифт для бланка")
        self.download_font_button.clicked.connect(self.download_font)
        self.layout.addWidget(self.download_font_button)

    def go_back(self):
        self.main_window.show_main_menu()

    def get_resource_path(self, relative_path):
        """ Получение пути к ресурсам в скомпилированном приложении """
        try:
            # Для скомпилированных приложений cx_Freeze
            base_path = sys._MEIPASS
        except Exception:
            # Для обычного запуска из исходников
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    def download_template(self):
        # Название и путь к шаблону
        template_name = 'Образец бланка.docx'
        template_path = self.get_resource_path(template_name)
        # Проверка наличия файла шаблона
        if not os.path.exists(template_path):
            QMessageBox.critical(self, "Ошибка", f"Файл шаблона {template_name} не найден.")
            return
        # Диалог для выбора пути сохранения
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить шаблон", template_name, "Word Files (*.docx)")
        if file_path:
            try:
                # Копирование файла шаблона в указанное место
                with open(template_path, "rb") as file_in, open(file_path, "wb") as file_out:
                    file_out.write(file_in.read())
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен в: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def download_font(self):
        # Название и путь к шрифту
        font_name = 'OMRBubbles.ttf'
        font_path = self.get_resource_path(font_name)
        # Проверка наличия файла шрифта
        if not os.path.exists(font_path):
            QMessageBox.critical(self, "Ошибка", f"Файл шрифта {font_name} не найден.")
            return
        # Диалог для выбора пути сохранения
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить шрифт", font_name, "Font Files (*.ttf)")
        if file_path:
            try:
                # Копирование файла шрифта в указанное место
                with open(font_path, "rb") as file_in, open(file_path, "wb") as file_out:
                    file_out.write(file_in.read())
                QMessageBox.information(self, "Успех", f"Файл шрифта успешно сохранен в: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить шрифт: {str(e)}")