import cv2
import matplotlib.pyplot as plt
import numpy as np
import pickle

import os
from pathlib import Path


def create_vector(data, img_name):
    ''' 
    Принимаем изображение и перерабатываем его в вектор,
    а после перерабатываем в строку что бы не потерять данные при 
    загрузке в БД.
    '''
    data_keys = list(data)
    BASE_DIR = Path(__file__).resolve().parent.parent # явное указание базовой директории
    base_image = f'{BASE_DIR}' + f'/{img_name}' # явно указываем путь до файла

    if 'width' in data_keys and 'height' in data_keys: # если имеем высоту и ширину в запросе
        width = int(data['width']) # ширина
        height = int(data['height']) # высота
        image = cv2.imread(base_image, cv2.IMREAD_COLOR)
        image = cv2.resize(image,(width,height))

    else: # если нам не дали длину и ширину, делаем как хотим
        width = 300 # можно сконифгурировать эти 2 параметра
        height = 300 # что бы задать размеры изображения по умолчанию
        image = cv2.imread(base_image, cv2.IMREAD_COLOR) 
        image = cv2.resize(image,(width,height))

    one_dimension_array = image.reshape(-1)
    normalized_array = one_dimension_array/255
    total = normalized_array.tostring()
    os.remove(f'{base_image}') # удаляем файл, что бы не засорять дисковое пространство
    return total


def reconstruct_vector(data):
    ''' Восстановление вектора из строки, в которой он хранится в БД.'''
    return np.fromstring(data, dtype=float)


def calc_distance(first, second):
    ''' Вычисление евклидова расстояния между векторами.'''
    # восстанавливаем вектора из строк
#    print(first[:100])
#    print(first[-10:])
#    print(second[:5])
#    print(second[-10:])
    first_vec = reconstruct_vector(first[1:])
    second_vec = reconstruct_vector(second[1:])

    distance = np.linalg.norm(first_vec-second_vec)

    return distance
