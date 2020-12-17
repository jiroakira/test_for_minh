# Generated by Django 3.1.4 on 2020-12-13 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0007_dichvukham_stt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chuoikham',
            name='lich_hen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='danh_sach_chuoi_kham', to='clinic.lichhenkham'),
        ),
        migrations.AlterField(
            model_name='dichvukham',
            name='bac_si_phu_trach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bac_si_phu_trach', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='chuc_nang',
            field=models.CharField(choices=[('1', 'Nguoi Dung'), ('2', 'Le Tan'), ('3', 'Bac Si Lam Sang'), ('4', 'Bac Si Chuyen Khoa'), ('5', 'Nhan vien Phong Tai Chinh'), ('6', 'Nhan vien Phong Thuoc'), ('7', 'Quan tri vien')], default='1', max_length=1),
        ),
    ]