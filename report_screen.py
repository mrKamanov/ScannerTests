from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import os
import matplotlib.pyplot as plt
from PySide6.QtGui import QPainter, QColor
import re

class ReportScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QHBoxLayout(self)  # Основной горизонтальный layout
        # Левый вертикальный layout для диаграммы и графика
        self.chart_layout = QVBoxLayout()
        self.layout.addLayout(self.chart_layout)
        # QLabel для диаграммы
        self.chart_view = QLabel()
        self.chart_layout.addWidget(self.chart_view)
        # QLabel для графика оценок
        self.grade_chart_view = QLabel()
        self.chart_layout.addWidget(self.grade_chart_view)
        # Правый вертикальный layout для отчета, кнопок и критериев
        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.right_layout)
        # Кнопка "Назад" и "Очистить отчет" (увеличены для читаемости)
        self.back_button = self.create_button("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.right_layout.addWidget(self.back_button)
        self.clear_button = self.create_button("Очистить")
        self.clear_button.clicked.connect(self.clear_report)
        self.right_layout.addWidget(self.clear_button)
        # Текстовое поле для отчета
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFixedWidth(300)  # Сужаем текстовое поле
        self.right_layout.addWidget(self.report_text)
        # Поля для ввода критериев оценки
        self.criteria_layout = QVBoxLayout()
        self.right_layout.addLayout(self.criteria_layout)
        self.label_criteria = QLabel("Оценочные критерии:")
        self.criteria_layout.addWidget(self.label_criteria)
        # Поля для ввода критериев
        self.input_5 = QLineEdit("90-100%")
        self.input_4 = QLineEdit("75-89%")
        self.input_3 = QLineEdit("50-74%")
        self.input_2 = QLineEdit("менее 50%")
        for input_field in [self.input_5, self.input_4, self.input_3, self.input_2]:
            input_field.setFixedWidth(80)  # Сужаем ширину полей
            self.criteria_layout.addWidget(input_field)
        # Кнопка "Обновить" для обновления отчета и диаграммы
        self.update_button = self.create_button("Обновить")
        self.update_button.clicked.connect(self.update_report)
        self.criteria_layout.addWidget(self.update_button)
        # Загрузка отчета при инициализации
        self.load_report()

    def create_button(self, text):
        """Создает увеличенную кнопку с читаемым текстом"""
        button = QPushButton(text)
        button.setFixedSize(150, 50)
        button.setStyleSheet("font-size: 16px;")
        return button

    def load_report(self):
        """Загружает отчет из файла 'report.txt' и генерирует диаграмму"""
        file_path = "report.txt"
        report_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                report_content = file.read()
            self.report_text.setText(report_content)
            self.generate_chart(report_content)  # Генерация диаграммы выполнения
            self.generate_grade_chart(report_content)  # Генерация графика оценок
        else:
            self.report_text.setText("Отчет не найден.")

    def clear_report(self):
        """Очищает содержимое файла report.txt и обновляет интерфейс"""
        file_path = "report.txt"
        if os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')
            self.report_text.setText('Отчет очищен.')
            self.chart_view.clear()
            self.grade_chart_view.clear()
        else:
            self.report_text.setText("Отчет не найден.")

    def update_report(self):
        """Обновляет отчет и отображаемые графики с учетом введенных критериев"""
        try:
            criteria_5 = self.input_5.text()
            criteria_4 = self.input_4.text()
            criteria_3 = self.input_3.text()
            criteria_2 = self.input_2.text()
            report_content = self.generate_report(criteria_5, criteria_4, criteria_3, criteria_2)
            self.report_text.setText(report_content)
            self.generate_chart(report_content)
            self.generate_grade_chart(report_content)
        except Exception as e:
            self.report_text.setText(f"Ошибка: {str(e)}")

    def generate_report(self, criteria_5, criteria_4, criteria_3, criteria_2):
        """Генерирует текст отчета с учетом введенных критериев"""
        file_path = "report.txt"
        if not os.path.exists(file_path):
            return "Отчет не найден."
        with open(file_path, 'r', encoding='utf-8') as file:
            report_content = file.read()
        work_data = re.findall(r"Работа (\d+).*?Всего вопросов: (\d+).*?Правильных ответов: (\d+)", report_content, re.DOTALL)
        updated_report = ""
        for work in work_data:
            work_number, total_questions, correct_answers = work
            total_questions = int(total_questions)
            correct_answers = int(correct_answers)
            percentage = (correct_answers / total_questions) * 100
            grade = self.grade_work(percentage, criteria_5, criteria_4, criteria_3, criteria_2)
            updated_report += f"Работа {work_number}\n"
            updated_report += f"Всего вопросов: {total_questions}\n"
            updated_report += f"Правильных ответов: {correct_answers}\n"
            updated_report += f"Процент выполнения: {percentage:.2f}%\n"
            updated_report += f"Оценка: {grade}\n\n"
        return updated_report

    def grade_work(self, percentage, criteria_5, criteria_4, criteria_3, criteria_2):
        """Оценивает работу в зависимости от процента и критериев"""
        if percentage >= self.parse_percentage(criteria_5):
            return "5"
        elif percentage >= self.parse_percentage(criteria_4):
            return "4"
        elif percentage >= self.parse_percentage(criteria_3):
            return "3"
        elif percentage >= self.parse_percentage(criteria_2):
            return "2"
        else:
            return "1"

    def parse_percentage(self, criteria_text):
        """Парсит текстовый критерий и возвращает минимальный процент для оценки"""
        try:
            min_percentage = float(criteria_text.split("-")[0].strip().replace("%", ""))
            return min_percentage
        except ValueError:
            return 0

    def generate_chart(self, report_content):
        """Генерирует и отображает диаграмму выполнения работ"""
        percentages = [float(match) for match in re.findall(r"Процент выполнения: (\d+\.\d+)%", report_content)]
        labels = [str(i + 1) for i in range(len(percentages))]
        plt.figure(figsize=(6, 4))
        plt.bar(labels, percentages, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        plt.xlabel("Работы")
        plt.ylabel("Процент выполнения")
        plt.title("Процент выполнения каждой работы")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()
        self.display_image("chart.png", self.chart_view)

    def generate_grade_chart(self, report_content):
        """Генерирует и отображает график оценок по работам"""
        grades = [int(match) for match in re.findall(r"Оценка: (\d)", report_content)]
        labels = [str(i + 1) for i in range(len(grades))]
        plt.figure(figsize=(6, 4))
        plt.plot(labels, grades, marker='o', linestyle='-', color='#1f77b4', markersize=8)
        plt.xlabel("Работы")
        plt.ylabel("Оценка")
        plt.title("Оценка по каждой работе")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("grade_chart.png")
        plt.close()
        self.display_image("grade_chart.png", self.grade_chart_view)

    def display_image(self, filepath, label):
        """Отображает изображение из файла в QLabel"""
        pixmap = QPixmap(filepath)
        label.setPixmap(pixmap)
        label.setScaledContents(True)

    def go_back(self):
        self.main_window.show_main_menu()