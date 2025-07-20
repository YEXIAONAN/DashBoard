from django.db import models

class User(models.Model):
    username = models.CharField(max_length=20, null=False, verbose_name="用户名")
    password = models.CharField(max_length=20, null=False, verbose_name="密码")
    gender = models.IntegerField(null=True, default=0, verbose_name="性别")
    age = models.IntegerField(null=True, verbose_name="年龄")
    phone = models.CharField(max_length=20, null=True, verbose_name="电话")
    email = models.EmailField(max_length=30, null=True, verbose_name="邮件")

    class Meta:
        db_table = "tb_user"
