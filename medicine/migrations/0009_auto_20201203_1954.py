# Generated by Django 3.1.4 on 2020-12-03 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0008_auto_20201203_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thuoc',
            name='loai_thau',
            field=models.CharField(blank=True, choices=[('1', 'Thầu tập trung'), ('2', 'Thầu riêng tại BV')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='thuoc',
            name='loai_thuoc',
            field=models.CharField(blank=True, choices=[('1', 'Tân Dược'), ('2', 'Chế phẩm YHCT'), ('3', 'Vị thuốc YHCT'), ('4', 'Phóng xạ')], max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='LoaiThau',
        ),
        migrations.DeleteModel(
            name='LoaiThuoc',
        ),
    ]
