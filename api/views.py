from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django.views.generic import View
from rest_framework import generics
from rest_framework import status
from django.shortcuts import get_object_or_404
from PIL import Image 

from .models import Person
from .serializers import PersonSerializer, InfoSerializer
from .utils import create_vector, calc_distance


class GetInfoOrDelete(generics.GenericAPIView):
    ''' 
    Модель для получения информации об объекте по его id
    или для удаления объекта по его id.
    '''
    def get(self, request, person_id):
        ''' 
        Запрос информации об объекте. 
        В случае успешного нахождения объекта возвращает JsonResponse
        в формате:
        {"first_name": "anytext",
        "last_name": "anytext",
        "is_vector": false/true}
        В случае отсутствия объекта в базе возвращает JsonResponse
        в формате:
        {"detail": "Not found."}
        '''
        data = get_object_or_404(Person, id=person_id)
        serializer = InfoSerializer(data)
        return Response(serializer.data)

    def delete(self, request, person_id):
        ''' 
        Запрос удаление объекта. 
        В случае успешного нахождения объекта возвращает JsonResponse
        в формате:
        {'success': True}
        В случае отсутствия объекта в базе возвращает JsonResponse
        в формате:
        {"detail": "Not found."}
        '''
        data = get_object_or_404(Person, id=person_id)
        data.delete()
        return JsonResponse({'success': True})


class GetAll(generics.GenericAPIView):
    '''
    Модель для запросов всех объектов модели Person 
    и создания новых записей.
    А так же для добавления векторов к записям, если изначально 
    запись была создана без него.
    '''
    queryset = Person.objects.all().values('id')
    
    def get(self, request):
        ''' Запрос всех объектов модели Person.'''
        
        queryset = self.get_queryset()
        if queryset:
            serializer = PersonSerializer(queryset, many=True)
            return Response(Person.objects.all().values('id'))
        
        else:
            return JsonResponse({'error':'empty base'})

    def post(self, request):
        ''' Создание объекта модели Person.
        Формат данных в запросе:
        first_name:str
        last_name:str
        vector: list or None
        Поля модели переварят и числовые данные, переданные в запросе,
        попутно превратив их в str формат.'''
        
        request_keys = list(request.data.keys())
        if 'first_name' in request_keys and 'last_name' in request_keys and ('vector' in request_keys): # на случай создания объета с вектором
            Person.objects.get_or_create(
                first_name=request.data['first_name'], # задаем имя  
                last_name=request.data['last_name'], # задаем фамилию  
                vector=request.data['vector'], # задаем вектор
                is_vector=True) # задаем признак наличия вектора
            queryset = Person.objects.filter(
                first_name=request.data['first_name'], 
                last_name=request.data['last_name'])
            serializer = PersonSerializer(queryset, many=True)
                
            return Response(serializer.data) # возвращаем id нового объекта

        if 'first_name' in request_keys and 'last_name' in request_keys: # если создается объект только с именем и фамилией
            Person.objects.get_or_create(
                first_name=request.data['first_name'], # задаем имя1
                last_name=request.data['last_name'], # задаем фамилию1
                is_vector=False) # задаем признак отсутствия вектора1

            queryset = Person.objects.filter(
                first_name=request.data['first_name'], 
                last_name=request.data['last_name'])
            serializer = PersonSerializer(queryset, many=True)
                
            return Response(serializer.data) # возвращаем id нового объекта

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        '''
        Метод на добавление вектора к записи в БД.
        Обязательные данные запроса:
        id:UUID
        file:image
        Название файла должно состоять из латинских букв и/или цифр и не должно содержать 
        пробелов, иначе утилита не сможет корректно прочитать файл и вернет ошибку.
        Дополнительные данные запроса (параметры на изменение размеров изображения):
        width:int
        height:int
        При отсутствии доп. данных размеры изображения меняются на 300х300.
        При добавлении вектора в поле таблицы вектор преобразуется в str (для удобства хранения)
        и меняется флаг is_vector на указывающий на наличие вектора у записи.
        '''
        main_keys = list(request.data.keys())
        if request.FILES['file'] and 'id' in main_keys:
            
            img = Image.open(request.FILES['file']) # открываем файл из запроса
            img_name = request.FILES['file'] # вытаскиваем имя что бы сохранить
            img = img.save(str(img_name)) # сохраняем файл под исходным именем с нужным расширением

            new_vector = create_vector(request.data, img_name) # преобразуем изображение в вектор
            obj_id = request.data['id'] # забираем id записи куда положить вектор
            trigger = get_object_or_404(Person, id=obj_id) # ищем запись (если ее нет, идем нафиг)
            
            if trigger:
                Person.objects.filter(id=obj_id).update(vector=new_vector, is_vector=True)
                return JsonResponse({'success': True})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CompareVectors(generics.GenericAPIView):
    '''
    Пока что единственное зачем нужен этот класс - сравнение двух векторов.
    Возможно потом добавится еще какой то функционал.
    '''
    def get(self, request):
        '''
        Метод на сравнение двух векторов.
        Принимает данные в формате:
        first_id:str
        second_id:str
        Возвращает данные в формате:
        {"distance": float}
        '''
        keys = list(request.data.keys())
        
        if 'first_id' not in keys and 'second_id' not in keys:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            # достаем id из запроса
            first_id = request.data['first_id']
            second_id = request.data['second_id']
            
            # достаем объекты по id
            first_obj = get_object_or_404(Person, id=first_id)
            second_obj = get_object_or_404(Person, id=second_id)

            # достаем вектора (пытаемся, по крайней мере)
            if first_obj.is_vector != 'false' and second_obj.is_vector != 'false':
                first_vec = first_obj.vector
                second_vec = second_obj.vector
                distance = calc_distance(first_vec, second_vec)
                return JsonResponse({'distance':distance})

            else: # если не получается возвращаем ответ с информацией где косяк
                return JsonResponse({'first_vector':first_obj.is_vector, 'second_vector':second_obj.is_vector})
