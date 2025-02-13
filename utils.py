# utils.py

import cv2
import numpy as np

# Функция для объединения изображений в одну панель
def stackImages(imgArray, scale, labels=[]):
    rows = len(imgArray)  # Количество строк изображений
    cols = len(imgArray[0])  # Количество столбцов изображений
    rowsAvailable = isinstance(imgArray[0], list)  # Проверяем, есть ли в строках вложенные списки
    width = imgArray[0][0].shape[1]  # Ширина первого изображения
    height = imgArray[0][0].shape[0]  # Высота первого изображения
    if rowsAvailable:
        # Если изображения вложены в список, выполняем ресайз для каждого изображения
        for x in range(0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)  # Масштабируем
                if len(imgArray[x][y].shape) == 2:  # Если изображение в черно-белом формате, конвертируем в цветное
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)  # Создаем пустое изображение для объединения
        hor = [imageBlank] * rows  # Массив для горизонтального объединения
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])  # Горизонтальное объединение изображений
        ver = np.vstack(hor)  # Вертикальное объединение строк
    else:
        # Если изображения не вложены в список
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)  # Масштабируем
            if len(imgArray[x].shape) == 2:  # Если изображение в черно-белом формате, конвертируем в цветное
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        ver = np.hstack(imgArray)  # Горизонтальное объединение изображений

    if labels:  # Если есть метки, рисуем их на изображениях
        eachImgWidth = int(ver.shape[1] / cols)  # Ширина каждой ячейки
        eachImgHeight = int(ver.shape[0] / rows)  # Высота каждой ячейки
        for d in range(0, rows):
            for c in range(0, cols):
                cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
                              (c * eachImgWidth + len(labels[d][c]) * 13 + 27, 30 + eachImgHeight * d),
                              (255, 255, 255), cv2.FILLED)  # Рисуем прямоугольник под метку
                cv2.putText(ver, labels[d][c], (eachImgWidth * c + 10, eachImgHeight * d + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)  # Рисуем текст метки
    return ver

# Функция для перестановки точек в нужном порядке
def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))  # Преобразуем в 4 точки
    myPointsNew = np.zeros((4, 1, 2), np.int32)  # Создаем новый массив для переставленных точек
    add = myPoints.sum(1)  # Находим сумму координат каждой точки
    myPointsNew[0] = myPoints[np.argmin(add)]  # Первая точка с минимальной суммой
    myPointsNew[3] = myPoints[np.argmax(add)]  # Точка с максимальной суммой
    diff = np.diff(myPoints, axis=1)  # Разница между координатами
    myPointsNew[1] = myPoints[np.argmin(diff)]  # Точка с минимальной разницей по координатам
    myPointsNew[2] = myPoints[np.argmax(diff)]  # Точка с максимальной разницей
    return myPointsNew

# Функция для фильтрации контуров, которые представляют собой прямоугольники
def rectContour(contours):
    rectCon = []
    for i in contours:
        area = cv2.contourArea(i)  # Вычисляем площадь контуров
        if area > 50:  # Пропускаем слишком маленькие контуры
            peri = cv2.arcLength(i, True)  # Периметр контура
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)  # Приближенная форма контура
            if len(approx) == 4:  # Если контур имеет 4 вершины (т.е. это прямоугольник)
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)  # Сортируем контуры по площади
    return rectCon

# Функция для получения углов прямоугольного контура
def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True)  # Периметр контура
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)  # Приближенная форма контура
    return approx

# Функция для разбиения изображения на сетку
def splitBoxes(img, questions, choices):
    if img.shape[0] % questions != 0 or img.shape[1] % choices != 0:
        raise ValueError("Изображение не может быть равномерно разделено на указанную сетку.")
    rows = np.vsplit(img, questions)  # Разбиваем изображение по строкам
    boxes = []
    for r in rows:
        cols = np.hsplit(r, choices)  # Разбиваем каждую строку на столбцы
        for box in cols:
            boxes.append(box)
    return boxes

# Функция для рисования сетки на изображении
def drawGrid(img, questions=5, choices=5):
    secW = img.shape[1] / choices  # Ширина одной ячейки
    secH = img.shape[0] / questions  # Высота одной ячейки
    for i in range(0, questions + 1):
        pt1 = (0, int(secH * i))  # Начало линии
        pt2 = (img.shape[1], int(secH * i))  # Конец линии
        cv2.line(img, pt1, pt2, (255, 255, 0), 2)  # Рисуем горизонтальные линии
    for i in range(0, choices + 1):
        pt1 = (int(secW * i), 0)  # Начало вертикальной линии
        pt2 = (int(secW * i), img.shape[0])  # Конец вертикальной линии
        cv2.line(img, pt1, pt2, (255, 255, 0), 2)  # Рисуем вертикальные линии
    return img

# Функция для отображения результатов проверки теста
def showAnswers(img, myIndex, grading, ans, questions=5, choices=5):
    secW = int(img.shape[1] / choices)  # Ширина одной ячейки
    secH = int(img.shape[0] / questions)  # Высота одной ячейки
    for x in range(0, questions):
        myAns = myIndex[x]  # Индекс выбранного ответа
        cX = (myAns * secW) + secW // 2  # Центр по оси X
        cY = (x * secH) + secH // 2  # Центр по оси Y
        if grading[x] == 1:  # Если ответ правильный
            myColor = (10, 255, 10)  # Мягкий зеленый цвет
            cv2.circle(img, (cX, cY), 30, myColor, cv2.FILLED)  # Рисуем круг с цветом
        else:  # Если ответ неправильный
            myColor = (10, 10, 255)  # Мягкий красный цвет
            cv2.circle(img, (cX, cY), 30, myColor, cv2.FILLED)  # Рисуем круг с цветом

            # Отображаем правильный ответ
            myColor = (10, 255, 10)  # Мягкий зеленый цвет для правильного ответа
            correctAns = ans[x]  # Индекс правильного ответа
            cv2.circle(img, ((correctAns * secW) + secW // 2, (x * secH) + secH // 2), 20, myColor, cv2.FILLED)  # Рисуем правильный ответ
