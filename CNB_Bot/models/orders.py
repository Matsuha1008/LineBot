from django.db import models


class Orders(models.Model):
    """
    訂單資訊
    """
    id = models.UUIDField(primary_key=True)
    user_id = models.CharField(max_length=255 , blank=False, default='')
    amount = models.IntegerField()
    is_pay = models.BooleanField(default=False)#預設為未付款
    transaction_id = models.CharField(max_length=255)

    created_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_time',)
        verbose_name = '訂單資訊'
        verbose_name_plural = verbose_name
    def __str__(self) -> str:
        return self.transaction_id





class Items(models.Model):
    """
    訂單項目資料
    """
    id = models.AutoField(primary_key=True)

    product_id = models.CharField(max_length=3, null=False)
    product_name = models.CharField(max_length=50)
    product_price = models.PositiveBigIntegerField()
    quantity = models.IntegerField()

    created_time = models.DateTimeField(auto_now=True)
    order_id = models.UUIDField(null=False)

    # product_id  → Products.id
    # order_id → Orders.id


    class Meta:
        ordering = ('-id',)
        verbose_name = '訂單項目資料'
        verbose_name_plural = verbose_name
    def __str__(self) -> str:
        return self.product_name
