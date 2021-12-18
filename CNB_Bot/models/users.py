from django.db import models


class User_Info(models.Model):
    """
    用戶資訊
    """

    user_id = models.CharField(max_length=255,null=False,default='')
    name = models.CharField(max_length=255,blank=True,null=False)
    image_url = models.CharField(max_length=255,null=False)    
    created_time  = models.DateTimeField(auto_now=True)

    #oders = models.ForeignKey(Orders, null=True, on_delete=models.SET_NULL)

    # 內嵌選項
    class Meta:
        ordering = ('-user_id',)
        verbose_name = '用戶資訊'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id