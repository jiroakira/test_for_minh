# from finance.models import HoaDonChuoiKham
# from clinic.views import hoa_don_dich_vu
import decimal
# from finance.models import HoaDonChuoiKham, HoaDonThuoc
import hashlib
import datetime
from bulk_update_or_create.query import BulkUpdateOrCreateQuerySet
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db.models.fields import AutoField, related
from django.utils import timezone, tree
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


def file_url(self, filename): 

    hash_ = hashlib.md5()
    hash_.update(str(filename).encode("utf-8") + str(datetime.datetime.now()).encode("utf-8"))
    file_hash = hash_.hexdigest()
    filename = filename
    return "%s%s/%s" % (self.file_prepend, file_hash, filename)

class UserManager(BaseUserManager):
    def create_user(self, ho_ten, so_dien_thoai, cmnd_cccd, dia_chi, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not so_dien_thoai:
            raise ValueError('Users must have an mobile number')

        if not ho_ten:
            raise ValueError('Users must have their name')

        user = self.model(
            so_dien_thoai=so_dien_thoai,
            ho_ten = ho_ten,
            cmnd_cccd = cmnd_cccd,
            dia_chi = dia_chi,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, ho_ten, so_dien_thoai, cmnd_cccd, dia_chi, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            so_dien_thoai=so_dien_thoai,
            password=password,
            ho_ten=ho_ten,
            cmnd_cccd = cmnd_cccd,
            dia_chi = dia_chi,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, ho_ten, so_dien_thoai, cmnd_cccd, dia_chi, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            so_dien_thoai=so_dien_thoai,
            password=password,
            ho_ten=ho_ten,
            cmnd_cccd = cmnd_cccd,
            dia_chi = dia_chi,
        )
        
        user.staff = True
        user.admin = True
        user.chuc_nang = 7
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    file_prepend = 'user/img/'
    GENDER = (
        ('Nam', "Nam"),
        ('Nữ', "Nu")
    )
    ROLE = (
        ('1', 'Nguoi Dung'),
        ('2', 'Le Tan'),
        ('3', 'Bac Si Lam Sang'),
        ('4', 'Bac Si Chuyen Khoa'),
        ('5', 'Nhan vien Phong Tai Chinh'),
        ('6', 'Nhan vien Phong Thuoc'),
        ('7', 'Quan tri vien')
    )
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    phone_regex = RegexValidator(regex=r"(84|0[3|5|7|8|9])+([0-9]{8})\b")
    so_dien_thoai = models.CharField(max_length=10, unique=True, validators=[phone_regex])
    ho_ten = models.CharField(max_length = 255)

    email = models.EmailField(null=True, unique=True)
    cmnd_cccd = models.CharField(max_length=13, null=True, unique = True)
    ngay_sinh = models.DateField(null=True, blank=True)
    gioi_tinh = models.CharField(choices=GENDER, max_length = 10, null=True, blank=True)
    anh_dai_dien = models.FileField(max_length=1000, upload_to=file_url, null=True, blank=True)
    dia_chi = models.TextField(max_length=1000, null=True, blank=True)
    chuc_nang = models.CharField(choices=ROLE, max_length = 1, default='1')
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that is built in.
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True, auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'so_dien_thoai'
    REQUIRED_FIELDS = ['ho_ten', 'cmnd_cccd', 'dia_chi',] # Email & Password are required by default.

    # def save(self, *agrs, **kwargs):
    #     ''' Khi được lưu lại thì sẽ update timestamp'''
    #     if not self.id:
    #         self.thoi_gian_tao = timezone.now()
    #     self.thoi_gian_chinh_sua = timezone.now()
    #     return super(User, self).save(*agrs, **kwargs)

    def __str__(self):              # __unicode__ on Python 2
        return self.ho_ten

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    def getSubName(self):
        lstChar = []
        lstString = self.ho_ten.split(' ')
        for i in lstString:
            lstChar.append(i[0].upper())
        subName = "".join(lstChar)
        return subName

class TinhTrangPhongKham(models.Model):
    """ Mở rộng phần tình trạng của phòng khám, khi phòng khám muốn tạm ngưng hoạt động
    trong một khoảng thời gian thì bảng này sẽ được sử dụng để mở rộng tính năng cho bảng Phòng Khám """
    kha_dung = models.BooleanField(default=True)
    thoi_gian_dong_cua = models.DateTimeField(null=True)
    thoi_gian_mo_cua = models.DateTimeField(null=True)

    # tọa độ địa lí của phòng khám sẽ được sử dụng để hiển thị lên map trong mobile app
    latitude = models.CharField(null=True, blank=True, max_length=50)
    longtitude = models.CharField(null=True, blank=True, max_length=50)

class PhongKham(models.Model):
    """ Thông tin chi tiết của phòng khám """
    ten_phong_kham = models.CharField(max_length = 255)
    dia_chi = models.TextField()
    so_dien_thoai = models.CharField(max_length = 12)
    email = models.EmailField()
    logo = models.URLField()
    tinh_trang = models.ForeignKey(TinhTrangPhongKham, on_delete=models.CASCADE)

class PhongChucNang(models.Model):
    """ Mỗi dịch vụ khám sẽ có một phòng chức năng riêng biệt, là nơi bệnh nhân sau khi được phân dịch vụ khám sẽ đến trong suốt chuỗi khám của bệnh nhân """
    ten_phong_chuc_nang = models.CharField(max_length=255)
    # bac_si_dam_nhan = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="bac_si_chuyen_khoa")
    # dich_vu_kham = models.ForeignKey(DichVuKham, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="phong_chuc_nang_theo_dich_vu")
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    def danh_sach_benh_nhan_theo_dich_vu_kham(self):
        # return self.dich_vu_kham.dich_vu_kham.all()
        return self.ten_phong_chuc_nang
    # def save(self, *agrs, **kwargs):
    #     if not self.id:
    #         self.thoi_gian_tao = timezone.now
    #     self.thoi_gian_cap_nhat = timezone.now
    #     return super(PhongChucNang, self).save(*agrs, **kwargs)

    # TODO review table PhongChucNang again

class DichVuKham(models.Model):
    """ Danh sách tất cả các dịch vụ khám trong phòng khám """
    ma_dvkt = models.CharField(max_length=50, null=True, blank=True)
    stt = models.CharField(max_length=10, null=True, blank=True, unique=True)
    ten_dvkt = models.CharField(max_length=255, null=True, blank=True)
    ma_gia = models.CharField(max_length=50, null=True, blank=True)
    don_gia = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=0)
    quyet_dinh = models.CharField(max_length=10, null=True, blank=True)
    cong_bo = models.CharField(max_length=10, null=True, blank=True)
    ma_cosokcb = models.CharField(max_length=20, null=True, blank=True)
    ten_dich_vu = models.CharField(max_length=255, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)
    bac_si_phu_trach = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bac_si_phu_trach", null=True, blank=True)
    # khoa_kham = models.ForeignKey(KhoaKham, on_delete=models.SET_NULL, related_name="khoa_kham", null=True, blank=True)
    phong_chuc_nang = models.ForeignKey(PhongChucNang, on_delete=models.SET_NULL, null=True, blank=True, related_name="dich_vu_kham_theo_phong")

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self):
        return self.ten_dvkt
class GiaDichVu(models.Model):
    """ Bảng giá sẽ lưu trữ tất cả giá của dịch vụ khám và cả thuốc """
    id_dich_vu_kham = models.OneToOneField(DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="gia_dich_vu_kham")
    gia = models.DecimalField(max_digits=10, decimal_places=3)  
    # id_thuoc = models.ForeignKey(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="gia_thuoc")
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(GiaDichVu, self).save(*agrs, **kwargs)

class BaoHiem(models.Model):
    """ Bảng Bảo Hiểm sẽ lưu trữ tất cả các loại bảo hiểm áp dụng trong phòng khám """
    ten_bao_hiem = models.CharField(max_length=255)
    # dạng bảo hiểm ở đây là số % được bảo hiểm chi trả
    dang_bao_hiem = models.SmallIntegerField(null=True, blank=True)
    id_dich_vu_kham = models.OneToOneField(DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="bao_hiem_dich_vu_kham")
    # id_thuoc = models.ForeignKey(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="bao_hiem_thuoc")
    thoi_gian_tao = models.DateTimeField()
    thoi_gian_chinh_sua = models.DateTimeField()

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(BaoHiem, self).save(*agrs, **kwargs)



class ProfilePhongChucNang(models.Model):
    phong_chuc_nang = models.OneToOneField(PhongChucNang, on_delete=models.CASCADE, related_name="profile_phong_chuc_nang")
    so_luong_cho = models.PositiveIntegerField(null=True, blank=True)
    thoi_gian_trung_binh = models.PositiveIntegerField(help_text="Đơn vị(phút)", null=True, blank=True)
    status = models.BooleanField(default=True)

@receiver(post_save, sender=PhongChucNang)
def create_or_update_func_room_profile(sender, instance, created, **kwargs):
    if created:
        ProfilePhongChucNang.objects.create(phong_chuc_nang=instance)
    instance.profile_phong_chuc_nang.save()

def get_sentinel_user():
    return User.objects.get_or_create(ho_ten='deleted')[0]

class TrangThaiLichHen(models.Model):
    ten_trang_thai = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.ten_trang_thai

# def get_default_trang_thai_lich_hen():
#     return TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Đã đặt trước")[0]

from datetime import timedelta

today = timezone.localtime(timezone.now())
tomorrow = today + timedelta(1)
today_start = today.replace(hour=0, minute=0, second=0)
today_end = tomorrow.replace(hour=0, minute=0, second=0)

# class LichHenKhamManager(models.Manager):
#     def lich_hen_hom_nay(self):
#         return self.filter(thoi_gian_bat_dau__lte = today_end, thoi_gian_ket_thuc__gte = today_start)

class LichHenKham(models.Model):
    # When you delete the referenced user, a user with the ho_ten of ‘deleted’ is assigned to the instance of MyModel that referenced it.
    benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="benh_nhan_hen_kham")
    nguoi_phu_trach = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), null=True, blank=True, related_name="nguoi_phu_trach")

    thoi_gian_bat_dau = models.DateTimeField()
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)

    trang_thai = models.ForeignKey(TrangThaiLichHen, on_delete=models.CASCADE, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True, auto_now=True)

    # objects = LichHenKhamManager()

class LichSuTrangThaiLichHen(models.Model):
    lich_hen_kham = models.ForeignKey(LichHenKham, on_delete=models.CASCADE, related_name="lich_hen")
    trang_thai_lich_hen = models.ForeignKey(TrangThaiLichHen, on_delete=models.CASCADE, related_name="trang_thai_lich_hen")
    # Nêu rõ nguyên nhân dẫn đến trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

def get_sentinel_dich_vu():
    return DichVuKham.objects.get_or_create(ten_dich_vu='deleted')[0]

class TrangThaiKhoaKham(models.Model):
    """ Tất cả các trạng thái có thể xảy ra trong phòng khám """
    trang_thai_khoa_kham = models.CharField(max_length=255)

    def __str__(self):
        return self.trang_thai_khoa_kham

class TrangThaiChuoiKham(models.Model):
    trang_thai_chuoi_kham = models.CharField(max_length=255)

    def __str__(self):
        return self.trang_thai_chuoi_kham

def get_default_trang_thai_chuoi_kham():
    return TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang chờ")[0]

def get_default_trang_thai_khoa_kham():
    return TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham="Đang chờ")[0]

class ChuoiKham(models.Model):
    """ Mỗi bệnh nhân khi tới phòng khám để sau khi khám tổng quát thì đều sẽ có một chuỗi khám.
    Do chuỗi khám này có tính tích lũy nên bệnh nhân có thể dễ dàng xem lại được lịch sử khám của mình kết hợp với các kết quả khám tại phòng khám """
    benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="chuoi_kham")
    bac_si_dam_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="bac_si_chuoi_kham", null=True, blank=True)
    lich_hen = models.ForeignKey(LichHenKham, on_delete=models.SET_NULL, null=True, blank=True)
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    thoi_gian_tai_kham = models.DateTimeField(null=True, blank=True)
    trang_thai = models.ForeignKey(TrangThaiChuoiKham, on_delete=models.CASCADE, related_name="trang_thai", null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True, blank=True, null=True)


class PhanKhoaKham(models.Model):
    benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    dich_vu_kham = models.ForeignKey(DichVuKham, on_delete=models.SET(get_sentinel_dich_vu), related_name="phan_khoa_dich_vu")
    bac_si_lam_sang = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="bac_si")
    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.CASCADE, null=True, blank=True, related_name="phan_khoa_kham")
    bao_hiem = models.BooleanField(default=False)
    priority = models.SmallIntegerField(null=True, blank=True)

    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)

    trang_thai = models.ForeignKey(TrangThaiKhoaKham, on_delete=models.SET_NULL, null=True)

    thoi_gian_tao = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)

    def gia_dich_vu_theo_bao_hiem(self):
        gia = self.dich_vu_kham.gia_dich_vu_kham.gia 
        if self.bao_hiem:
            tong_tien = gia * decimal.Decimal((1 - (self.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem / 100)))
        else:
            tong_tien = gia
        return tong_tien

    def gia(self):
        return self.dich_vu_kham.gia_dich_vu_kham.gia 

    def muc_bao_hiem(self):
        return self.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem

class LichSuTrangThaiKhoaKham(models.Model):
    phan_khoa_kham = models.ForeignKey(PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai_khoa_kham = models.ForeignKey(TrangThaiKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    # Nêu rõ nguyên nhân dẫn tới trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)
    
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class LichSuChuoiKham(models.Model):
    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai = models.ForeignKey(TrangThaiChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    # Nêu rõ nguyên nhân dẫn tới trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)
    
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class KetQuaTongQuat(models.Model):
    """ Kết quả tổng quát của người dùng sau một lần đến thăm khám tại phòng khám """
    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.SET_NULL, null=True, related_name="ket_qua_tong_quat")
    # benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    ma_ket_qua = models.CharField(max_length=50, null=True, blank=True)
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

class KetQuaChuyenKhoa(models.Model):
    """ Kết quả của khám chuyên khoa mà người dùng có thể nhận được """ 
    ma_ket_qua = models.CharField(max_length=50, null=True, blank=True, unique=True)
    ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.CASCADE, related_name="ket_qua_chuyen_khoa")
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

class FileKetQua(models.Model):
    """ File kết quả của mỗi người dùng """
    file_prepend = 'user/documents/'
    file = models.FileField(upload_to=file_url, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.file.url
    # ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_chuyen_khoa")
    # ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_tong_quat")

class FileKetQuaTongQuat(models.Model):
    file = models.ForeignKey(FileKetQua, on_delete=models.CASCADE, related_name="file_tong_quat")
    ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.CASCADE, related_name="file_ket_qua_tong_quat")

class FileKetQuaChuyenKhoa(models.Model):
    file = models.ForeignKey(FileKetQua, on_delete=models.CASCADE, related_name="file_chuyen_khoa")
    ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.CASCADE, related_name="file_ket_qua_chuyen_khoa")

class BaiDang(models.Model):
    tieu_de = models.TextField(null=True, blank=True)
    hinh_anh = models.ImageField(upload_to = file_url, null=True, blank=True)
    tom_tat = models.TextField(null=True, blank=True)
    noi_dung = models.TextField(null=True, blank=True)
    