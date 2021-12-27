from django.db import models


class Category(models.Model):
    """
    商品類別
    """
    name = models.CharField(verbose_name='商品類別', max_length=20)
    class Meta:
        verbose_name = '商品類別'
        verbose_name_plural = verbose_name
    def __str__(self) -> str:
        return self.name


class Products(models.Model):
    """
    商品資訊
    """

    id = models.CharField(max_length=3, null=False, primary_key=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    price = models.PositiveBigIntegerField()
    description = models.TextField(blank=True)
    image_url = models.TextField(blank=False)
    created_time  = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-id',)
        verbose_name = '商品資訊'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
