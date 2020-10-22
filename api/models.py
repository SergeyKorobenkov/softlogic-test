from django.db import models
import uuid

# Create your models here.


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50) # имя
    last_name = models.CharField(max_length=50) # фамилия
    vector = models.TextField() # тут хранится вектор
    is_vector = models.BooleanField() # тут хранится признак наличия/отсутствия вектора
    
    def __str__(self):
        return self.post_id