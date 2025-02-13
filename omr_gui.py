from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QCheckBox, QMessageBox, QHBoxLayout, QScrollArea, QSplitter
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtCore import QTimer, Qt
import cv2
import os
from video_processing import process_video_frame

class OMRApp(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Конфигурация OMR сетки и видео")
        # Значения по умолчанию
        self.questions = 5
        self.choices = 5
        self.correct_answers = [1, 2, 0, 2, 4]
        self.image_size = 700
        # Основной макет с разделителем
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.splitter)
        # Левая часть - вертикальный макет для видео и результата
        self.left_layout = QVBoxLayout()
        self.video_widget = QWidget()
        self.video_widget_layout = QVBoxLayout(self.video_widget)
        self.video_widget_layout.setAlignment(Qt.AlignCenter)
        self.splitter.addWidget(self.video_widget)
        # Метка для отображения результатов
        self.result_label = QLabel("Результат: N/A")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.video_widget_layout.addWidget(self.result_label)
        # Метка для видео
        self.video_label = QLabel()
        self.video_widget_layout.addWidget(self.video_label)
        # Правая часть - панель управления
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        # Кнопка "Скрыть панель"
        self.toggle_panel_button = QPushButton("Скрыть панель")
        self.toggle_panel_button.setIcon(QIcon("icons/panel.png"))
        self.toggle_panel_button.clicked.connect(self.toggle_control_panel)
        self.right_layout.addWidget(self.toggle_panel_button)
        # Кнопка "Показать панель"
        self.return_panel_button = QPushButton("Показать панель")
        self.return_panel_button.setIcon(QIcon("icons/return.png"))
        self.return_panel_button.clicked.connect(self.toggle_control_panel)
        self.return_panel_button.hide()
        self.main_layout.addWidget(self.return_panel_button, alignment=Qt.AlignCenter)
        # Кнопка для скрытия/показа видео
        self.toggle_video_button = QPushButton("Скрыть видео")
        self.toggle_video_button.setIcon(QIcon("icons/video.png"))
        self.toggle_video_button.clicked.connect(self.toggle_video_display)
        self.right_layout.addWidget(self.toggle_video_button)
        # Кнопка "Назад" для возвращения в главное меню
        self.back_button = QPushButton("Назад")
        self.back_button.setIcon(QIcon("icons/back.png"))
        self.back_button.clicked.connect(self.go_back)
        self.right_layout.addWidget(self.back_button)
        # Кнопка для создания стоп-кадра
        self.capture_button = QPushButton("Создать стоп-кадр")
        self.capture_button.clicked.connect(self.toggle_pause_video)
        self.right_layout.addWidget(self.capture_button)
        # Кнопка "Добавить в отчет", активируется только при наличии стоп-кадра
        self.report_button = QPushButton("Добавить в отчет")
        self.report_button.setEnabled(False)  # Активируется только при наличии стоп-кадра
        self.report_button.clicked.connect(self.save_report)
        self.right_layout.addWidget(self.report_button)
        # Поля ввода для количества вопросов и вариантов
        self.questions_label = QLabel("Количество вопросов:")
        self.questions_entry = QLineEdit(str(self.questions))
        self.choices_label = QLabel("Количество вариантов:")
        self.choices_entry = QLineEdit(str(self.choices))
        self.apply_button = QPushButton("Применить")
        self.update_button = QPushButton("Обновить")
        # Добавление элементов управления в макет
        self.right_layout.addWidget(self.questions_label)
        self.right_layout.addWidget(self.questions_entry)
        self.right_layout.addWidget(self.choices_label)
        self.right_layout.addWidget(self.choices_entry)
        self.right_layout.addWidget(self.apply_button)
        self.right_layout.addWidget(self.update_button)
        # Область для чекбоксов с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.right_layout.addWidget(self.scroll_area)
        self.checkbox_layout = QGridLayout(self.scroll_widget)
        self.create_checkboxes()
        # Добавление панели в разделитель
        self.splitter.addWidget(self.right_widget)
        # Таймер и состояние камеры
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video)
        self.is_paused = False
        self.paused_frame = None
        # Подключение сигналов
        self.apply_button.clicked.connect(self.apply_settings)
        self.update_button.clicked.connect(self.update_correct_answers)
        # Стили QSS
        self.set_styles()

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
        self.main_window.show_main_menu()

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
                self.questions,
                self.choices,
                self.correct_answers,
                self.image_size
            )
            incorrect_answers = self.questions - correct_answers
            # Подготавливаем текст для нового отчета
            new_report_text = (
                f"Всего вопросов: {self.questions}\n"
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

    def apply_settings(self):
        try:
            questions = int(self.questions_entry.text())
            if questions <= 0:
                raise ValueError("Количество вопросов должно быть положительным целым числом.")
            self.questions = questions
            choices = int(self.choices_entry.text())
            if choices <= 0:
                raise ValueError("Количество вариантов должно быть положительным целым числом.")
            self.choices = choices
            self.create_checkboxes()
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", str(e))

    def add_report_to_screen(self):
        """Добавляет новый отчет о результатах теста на экран отчета."""
        if self.paused_frame is None:
            QMessageBox.warning(self, "Ошибка", "Стоп-кадр не создан.")
            return
        try:
            # Обрабатываем стоп-кадр и получаем результаты
            imgFinal, correct_answers, score = process_video_frame(
                self.paused_frame,
                self.questions,
                self.choices,
                self.correct_answers,
                self.image_size
            )
            incorrect_answers = self.questions - correct_answers
            # Подготавливаем текст для нового отчета
            work_number = self.main_window.report_screen.report_text.toPlainText().count("Работа") + 1
            new_report_text = (
                f"Работа {work_number}\n"
                f"Всего вопросов: {self.questions}\n"
                f"Правильных ответов: {correct_answers}\n"
                f"Неправильных ответов: {incorrect_answers}\n"
                f"Процент выполнения: {score:.2f}%\n\n"
            )
            # Добавляем новый отчет в текстовое поле отчета
            current_content = self.main_window.report_screen.report_text.toPlainText()
            updated_content = current_content + new_report_text
            self.main_window.report_screen.load_report(updated_content)
            QMessageBox.information(self, "Отчет", f"Отчет успешно добавлен как 'Работа {work_number}'.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет: {e}")

    def update_correct_answers(self):
        try:
            self.correct_answers = []
            for i, row_vars in enumerate(self.checkbox_vars):
                selected = [j for j, var in enumerate(row_vars) if var.isChecked()]
                if len(selected) == 1:
                    self.correct_answers.append(selected[0])
                else:
                    raise ValueError(f"Вопрос {i + 1} должен иметь ровно один правильный ответ.")
            QMessageBox.information(self, "Успех", "Настройки успешно обновлены!")
            if self.paused_frame is not None:
                self.analyze_paused_frame()
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", str(e))

    def analyze_paused_frame(self):
        if self.paused_frame is not None:
            imgFinal, correct_answers, score = process_video_frame(self.paused_frame, self.questions, self.choices, self.correct_answers, self.image_size)
            imgRGB = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2RGB)
            h, w, ch = imgRGB.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(imgRGB.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
            self.result_label.setText(f"Результат: {correct_answers}/{self.questions}, {score:.2f}%")

    def update_video(self):
        if not self.video_label.isVisible():
            return
        success, img = self.cap.read()
        if success:
            imgFinal, correct_answers, score = process_video_frame(img, self.questions, self.choices, self.correct_answers, self.image_size)
            imgRGB = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2RGB)
            h, w, ch = imgRGB.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(imgRGB.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
            self.result_label.setText(f"Результат: {correct_answers}/{self.questions}, {score:.2f}%")

    def create_checkboxes(self):
        while self.checkbox_layout.count():
            child = self.checkbox_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.checkbox_vars = []
        for i in range(self.questions):
            question_label = QLabel(f"Вопрос {i + 1}")
            self.checkbox_layout.addWidget(question_label, i, 0)
            row_vars = []
            for j in range(self.choices):
                var = QCheckBox()
                self.checkbox_layout.addWidget(var, i, j + 1)
                row_vars.append(var)
            self.checkbox_vars.append(row_vars)

    def toggle_control_panel(self):
        if self.right_widget.isVisible():
            # Скрываем панель и показываем кнопку "Показать панель"
            self.right_widget.hide()
            self.return_panel_button.show()
            self.splitter.setSizes([1, 0])  # Оставляем только левую часть
            self.toggle_panel_button.setText("Показать панель")
        else:
            # Показываем панель и скрываем кнопку "Показать панель"
            self.right_widget.show()
            self.return_panel_button.hide()
            self.splitter.setSizes([1, 1])  # Восстанавливаем обе части
            self.toggle_panel_button.setText("Скрыть панель")

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