import os

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
import cv2
from video_processing import process_video_frame

class VideoControls(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("video_controls")
        self.video_widget = QWidget()
        self.video_widget_layout = QVBoxLayout(self.video_widget)
        self.video_widget_layout.setAlignment(Qt.AlignCenter)
        self.result_label = QLabel("Результат: N/A")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.video_widget_layout.addWidget(self.result_label)
        self.video_label = QLabel()
        self.video_widget_layout.addWidget(self.video_label)
        self.toggle_video_button = QPushButton("Скрыть видео")
        self.toggle_video_button.setIcon(QIcon("icons/video.png"))
        self.toggle_video_button.clicked.connect(self.toggle_video_display)
        self.video_widget_layout.addWidget(self.toggle_video_button)
        self.capture_button = QPushButton("Создать стоп-кадр")
        self.capture_button.clicked.connect(self.toggle_pause_video)
        self.video_widget_layout.addWidget(self.capture_button)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video)
        self.cap = None  # Камера не активна по умолчанию
        self.is_paused = False
        self.paused_frame = None

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(10, 160)
        self.timer.start(10)

    def stop_camera(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        self.video_label.clear()

    def go_back(self):
        self.stop_camera()
        self.parent.show_main_menu()

    def toggle_pause_video(self):
        """Переключение состояния паузы видеопотока."""
        if self.is_paused:
            self.timer.start(10)
            self.capture_button.setText("Создать стоп-кадр")
            self.report_button.setEnabled(False)
        else:
            self.timer.stop()
            self.capture_button.setText("Продолжить видео")
            success, frame = self.cap.read()
            if success:
                self.paused_frame = frame
                self.report_button.setEnabled(True)  # Активируем кнопку "Добавить в отчет"
        self.is_paused = not self.is_paused

    def save_report(self):
        """Добавляет новый отчет о результатах теста в конец файла report.txt, с последовательной нумерацией."""
        if self.paused_frame is None:
            QMessageBox.warning(self, "Ошибка", "Стоп-кадр не создан.")
            return
        try:
            # Обрабатываем стоп-кадр и получаем результаты
            imgFinal, correct_answers, score = process_video_frame(
                self.paused_frame,
                self.parent.questions,
                self.parent.choices,
                self.parent.correct_answers,
                self.parent.image_size
            )
            incorrect_answers = self.parent.questions - correct_answers
            # Подготавливаем текст для нового отчета
            new_report_text = (
                f"Всего вопросов: {self.parent.questions}\n"
                f"Правильных ответов: {correct_answers}\n"
                f"Неправильных ответов: {incorrect_answers}\n"
                f"Процент выполнения: {score:.2f}%\n\n"
            )
            # Определяем номер следующей работы
            file_path = "report.txt"
            work_number = 1
            # Если файл существует, подсчитываем количество "Работа N" и увеличиваем счетчик
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                work_number = content.count("Работа") + 1
            # Добавляем заголовок для новой записи
            new_report_text = f"Работа {work_number}\n" + new_report_text
            # Добавляем новый отчет в конец файла
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(new_report_text)
            QMessageBox.information(self, "Отчет",
                                   f"Отчет успешно добавлен в файл report.txt как 'Работа {work_number}'.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет: {e}")

    def update_video(self):
        if not self.video_label.isVisible():
            return
        success, img = self.cap.read()
        if success:
            imgFinal, correct_answers, score = process_video_frame(img, self.parent.questions, self.parent.choices, self.parent.correct_answers, self.parent.image_size)
            imgRGB = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2RGB)
            h, w, ch = imgRGB.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(imgRGB.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
            self.result_label.setText(f"Результат: {correct_answers}/{self.parent.questions}, {score:.2f}%")

    def toggle_video_display(self):
        if self.video_label.isVisible():
            self.video_label.hide()
            self.toggle_video_button.setText("Показать видео")
        else:
            self.video_label.show()
            self.toggle_video_button.setText("Скрыть видео")

    def set_styles(self):
        # Здесь добавляем стили через QSS
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                background-color: #2E3440;
                color: #ECEFF4;
            }
            #right_widget {
                background-color: #3B4252;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            QPushButton {
                background-color: #4C566A;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                margin: 8px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QLabel {
                font-size: 18px;
                margin: 5px;
                color: #f2dada;
            }
            QLineEdit {
                padding: 8px;
                font-size: 16px;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin: 10px;
            }
            QCheckBox {
                font-size: 16px;
                margin: 10px;
            }
            QScrollArea {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QSplitter::handle {
                background-color: #f2dada;
                width: 10px;
                border: none;
            }
        """)