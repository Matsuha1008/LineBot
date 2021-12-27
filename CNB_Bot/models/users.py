from django.db import models


class User_Info(models.Model):
    """
    用戶資訊
    """

    user_id = models.CharField(max_length=255 , blank=False, default='', primary_key=True)
    name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)    
    created_time  = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-user_id',)
        verbose_name = '用戶資訊'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id
