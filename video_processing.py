import cv2  # Импортируем библиотеку OpenCV для работы с изображениями и видео
import numpy as np  # Импортируем библиотеку NumPy для работы с массивами
import utils  # Импортируем вспомогательные функции из модуля utils

def process_video_frame(img, questions, choices, correct_answers, image_size):
    # Изменяем размеры изображения так, чтобы оно подходило под заданное количество вопросов и вариантов
    new_width = choices * (image_size // choices)
    new_height = questions * (image_size // questions)
    img = cv2.resize(img, (new_width, new_height))  # Изменяем размер изображения
    imgFinal = img.copy()  # Копируем исходное изображение для дальнейшей обработки
    imgBlank = np.zeros((new_height, new_width, 3), np.uint8)  # Создаем пустое изображение для рисования
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Преобразуем изображение в оттенки серого
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # Применяем гауссово размытие для улучшения обнаружения контуров
    imgCanny = cv2.Canny(imgBlur, 10, 70)  # Применяем детектор Канни для нахождения контуров

    try:
        imgContours = img.copy()  # Копируем изображение для рисования контуров
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # Находим контуры на изображении
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # Рисуем контуры на изображении
        rectCon = utils.rectContour(contours)  # Фильтруем контуры, оставляя только прямоугольники
        if len(rectCon) < 1:  # Если не удалось найти прямоугольники, выбрасываем исключение
            raise Exception("Не удалось найти достаточное количество контуров.")

        biggestPoints = utils.getCornerPoints(rectCon[0])  # Находим углы самого большого прямоугольника

        if biggestPoints.size != 0:  # Если углы найдены
            biggestPoints = utils.reorder(biggestPoints)  # Переносим углы в правильном порядке
            cv2.drawContours(imgContours, biggestPoints, -1, (0, 255, 0), 20)  # Рисуем углы на изображении
            pts1 = np.float32(biggestPoints)  # Преобразуем углы в формат float32 для преобразования перспективы
            pts2 = np.float32([[0, 0], [new_width, 0], [0, new_height], [new_width, new_height]])  # Целевые точки для преобразования
            matrix = cv2.getPerspectiveTransform(pts1, pts2)  # Получаем матрицу преобразования перспективы
            imgWarpColored = cv2.warpPerspective(img, matrix, (new_width, new_height))  # Применяем преобразование перспективы

            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)  # Преобразуем изображение в черно-белое
            imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]  # Применяем пороговое преобразование для выделения области

            boxes = utils.splitBoxes(imgThresh, questions, choices)  # Разбиваем изображение на отдельные клетки
            myPixelVal = np.zeros((questions, choices))  # Создаем массив для хранения количества белых пикселей в каждой клетке
            for i, image in enumerate(boxes):
                totalPixels = cv2.countNonZero(image)  # Подсчитываем количество белых пикселей в клетке
                myPixelVal[i // choices][i % choices] = totalPixels  # Заполняем массив пикселей

            myIndex = [np.argmax(row) for row in myPixelVal]  # Находим индекс клетки с максимальным количеством пикселей (выбранный вариант)

            # Оценка правильности ответов
            grading = [1 if correct_answers[i] == myIndex[i] else 0 for i in range(questions)]
            score = (sum(grading) / questions) * 100  # Рассчитываем процент правильных ответов

            # Отображаем результаты на изображении
            utils.showAnswers(imgWarpColored, myIndex, grading, correct_answers, questions, choices)
            utils.drawGrid(imgWarpColored, questions, choices)  # Рисуем сетку на изображении
            imgRawDrawings = np.zeros_like(imgWarpColored)  # Создаем пустое изображение для рисования контуров
            cv2.drawContours(imgRawDrawings, contours, -1, (0, 255, 0), 20)  # Рисуем контуры на изображении

            return imgWarpColored, sum(grading), score  # Возвращаем итоговое изображение, количество правильных ответов и процент

        else:
            raise Exception("Не удалось найти правильные контуры.")  # Если не удалось найти правильные контуры

    except Exception as e:  # В случае ошибки
        print(f"Ошибка: {e}")  # Выводим сообщение об ошибке
        return img, 0, 0  # Возвращаем исходное изображение и нулевые значения для правильных ответов и процента
