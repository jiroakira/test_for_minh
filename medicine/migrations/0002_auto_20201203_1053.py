# Generated by Django 3.1.3 on 2020-12-03 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thuoc',
            name='gia_ban',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='gia_mua',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='han_su_dung',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='ma_thuoc',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='mo_ta',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='ngay_san_xuat',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='quy_cach',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='so_ke_tai_quay',
        ),
        migrations.RemoveField(
            model_name='thuoc',
            name='tac_dung_phu',
        ),
        migrations.AddField(
            model_name='thuoc',
            name='don_gia',
            field=models.CharField(max_length=50, null=True, verbose_name='Đơn giá'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='don_gia_tt',
            field=models.CharField(max_length=50, null=True, verbose_name='Đơn giá thành tiền'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='don_vi_tinh',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Đơn vị tính'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='dong_goi',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Đóng gói'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='duong_dung',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Đường dùng'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='ham_luong',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Hàm lượng'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='hang_sx',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='loai_thau',
            field=models.CharField(blank=True, choices=[('1', 'Thầu tập trung'), ('2', 'Thầu riêng tại BV')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='ma_cskcb',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='ma_hoat_chat',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Mã hoạt chất'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='nhom_thau',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='nuoc_sx',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='quyet_dinh',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='so_dang_ky',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Số đăng ký'),
        ),
        migrations.AddField(
            model_name='thuoc',
            name='ten_hoat_chat',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Tên hoạt chất'),
        ),
        migrations.AlterField(
            model_name='congty',
            name='dia_chi',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Địa chỉ'),
        ),
        migrations.AlterField(
            model_name='congty',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Email công ty'),
        ),
        migrations.AlterField(
            model_name='congty',
            name='giay_phep_kinh_doanh',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Giấy phép kinh doanh'),
        ),
        migrations.AlterField(
            model_name='congty',
            name='mo_ta',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Mô tả công ty'),
        ),
        migrations.AlterField(
            model_name='congty',
            name='so_lien_lac',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Số liên lạc'),
        ),
        migrations.AlterField(
            model_name='thuoc',
            name='loai_thuoc',
            field=models.CharField(blank=True, choices=[('1', 'Tân Dược'), ('2', 'Chế phẩm YHCT'), ('3', 'Vị thuốc YHCT'), ('4', 'Phóng xạ')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='thuoc',
            name='ten_thuoc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Tên thuốc'),
        ),
    ]