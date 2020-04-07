#encode utf-8
from django.db import models


class BaseModel(models.Model):

    create_time = models.DateField(auto_now_add=True, verbose_name='建表日期')
    update_time = models.DateField(auto_now_add=True, verbose_name='更新日期')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        # 是抽象类
        abstract = True
