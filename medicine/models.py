from datetime import time
import decimal
from django.db import models
import uuid
# from django.contrib.auth import get_user_model
from django.utils import timezone
from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# User = get_user_model()

class CongTy(models.Model):
    id = models.AutoField(primary_key=True)
    
    ten_cong_ty = models.CharField(max_length=255, verbose_name="Tên Công Ty")
    giay_phep_kinh_doanh = models.CharField(max_length=255, verbose_name="Giấy phép kinh doanh", null=True, blank=True)
    dia_chi = models.CharField(max_length=255, verbose_name="Địa chỉ", null=True, blank=True)
    so_lien_lac = models.CharField(max_length=255, verbose_name="Số liên lạc", null=True, blank=True)
    email = models.CharField(max_length=255, verbose_name="Email công ty", null=True, blank=True)
    mo_ta = models.CharField(max_length=255, verbose_name="Mô tả công ty", null=True, blank=True)
    
    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Công Ty'
        verbose_name_plural = 'Công Ty'

    def __str__(self):
        return self.ten_cong_ty
# class LoaiThuoc(models.Model): 
    
#     loai_thuoc = models.CharField(max_length=255, choices=TYPE_CHOICES)
class NhomThau(models.Model):
    ten_nhom_thau = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.ten_nhom_thau

class Thuoc(models.Model):
    TYPE_CHOICES_LOAI_THUOC = (
        ('1', 'Tân Dược'),
        ('2', 'Chế phẩm YHCT'),
        ('3', 'Vị thuốc YHCT'),
        ('4', 'Phóng xạ'),
    )
    TYPE_CHOICES_LOAI_THAU = (
        ('1', 'Thầu tập trung'),
        ('2', 'Thầu riêng tại BV')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    ma_thuoc = models.IntegerField(unique=True, blank=True, null=True)
    ma_hoat_chat = models.CharField(max_length=15, null=True, blank=True, verbose_name="Mã hoạt chất")
    ten_hoat_chat = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên hoạt chất")
    duong_dung = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đường dùng")
    ham_luong = models.CharField(max_length=50, null=True, blank=True, verbose_name="Hàm lượng")
    ten_thuoc = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên thuốc")    
    # ma_thuoc = models.CharField(max_length=200, null=True, blank=True, verbose_name="Mã thuốc") # mã thuốc được sử dụng khi tồn tại 2 loại thuốc giống nhau nhưng khác công ty
    # loai_thuoc = models.CharField(max_length=100, null=True, blank=True, verbose_name="Loại thuốc") # có rất nhiều loại thuốc khác nhau: viên nén/viên nang/siro/....
    so_dang_ky = models.CharField(max_length=50, null=True, blank=True, verbose_name="Số đăng ký")
    dong_goi = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đóng gói")
    don_vi_tinh = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đơn vị tính")
    don_gia = models.CharField(max_length=50, null=True, verbose_name="Đơn giá")
    don_gia_tt = models.CharField(max_length=50, null=True, verbose_name="Đơn giá thành tiền")
    so_lo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Số Lô")
    so_luong_kha_dung = models.IntegerField(verbose_name="Số lượng khả dụng") # Số lượng thuốc khả dụng sau khi đã bán hoặc trả lại thuốc 
    # Để kiểm soát và duy trì truy xuất nguồn gốc, số lô được chỉ định và cũng giúp kiểm tra thời hạn sử dụng và các vấn đề khác
    # Thuốc có thời hạn sử dụng là 3 năm nên tùy theo nhu cầu sử dụng và cách tiêu dùng mà cơ sở sản xuất có lịch sản xuất.. 
    ma_cskcb = models.CharField(max_length=50, null=True, blank=True)
    hang_sx = models.CharField(max_length=255, null=True, blank=True)
    nuoc_sx = models.CharField(max_length=50, null=True, blank=True)
    cong_ty = models.ForeignKey(CongTy, on_delete=models.CASCADE, related_name="thuoc_cong_ty", null=True, blank=True)
    quyet_dinh = models.CharField(max_length=10, null=True, blank=True)
    loai_thuoc = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_THUOC, null=True, blank = True)
    cong_bo = models.CharField(max_length=50, null=True, blank=True)
    loai_thau = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_THAU, null = True, blank = True)
    nhom_thau = models.ForeignKey(NhomThau, on_delete=models.SET_NULL, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False, null=True, blank=True)
    # so_ke_tai_quay = models.CharField(max_length=255, null=True, blank=True, verbose_name="Số Kệ") # Để có thể biết được vị trí thuốc này đang được đặt chỗ nào trong quầy thuốc.
    # han_su_dung = models.DateField(null=True, blank=True, verbose_name="Hạn sử dụng") # Hạn sử dụng
    # ngay_san_xuat = models.DateField(null=True, blank=True, verbose_name="Ngày sản xuất") # Ngày sản xuất
    # mo_ta = models.CharField(max_length=255, verbose_name="Mô tả")
    # tac_dung_phu = models.CharField(max_length=255, verbose_name="Tác dụng phụ")
    # quy_cach = models.IntegerField(verbose_name="Quy cách đóng gói") # số lượng đóng gói
    # qty_in_strip=models.IntegerField()
    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Thuốc"
        verbose_name_plural = "Thuốc"

    def __str__(self):
        return self.ten_thuoc

    @property
    def kha_dung(self):
        return self.so_luong_kha_dung > 0
    
def get_sentinel_user():
    return User.objects.get_or_create(ho_ten='deleted')[0]

def get_sentinel_thuoc():
    return Thuoc.objects.get_or_create(ten_thuoc='deleted')[0]

class GiaThuoc(models.Model):
    """ Bảng Giá sẽ lưu trữ tất cả giá của thuốc"""
    id_thuoc = models.OneToOneField(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="gia_thuoc")
    gia = models.DecimalField(max_digits=10, decimal_places=3)   
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(GiaThuoc, self).save(*agrs, **kwargs)
    
class BaoHiemThuoc(models.Model):
    id_thuoc = models.OneToOneField(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="bao_hiem_thuoc")
    muc_bao_hiem = models.PositiveIntegerField() 
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(BaoHiemThuoc, self).save(*agrs, **kwargs)

class TrangThaiDonThuoc(models.Model):
    trang_thai = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Trạng Thái Đơn Thuốc"
        verbose_name_plural = "Trạng Thái Đơn Thuốc"

def get_default_trang_thai_don_thuoc():
    return TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đang Chờ")[0]

class DonThuoc(models.Model):
    benh_nhan = models.ForeignKey("clinic.User", on_delete=models.SET(get_sentinel_user), related_name="don_thuoc")
    bac_si_ke_don = models.ForeignKey("clinic.User", on_delete=models.SET(get_sentinel_user), related_name="bac_si_ke_don")
    ma_don_thuoc = models.CharField(max_length=50, unique=True)
    trang_thai = models.ForeignKey(TrangThaiDonThuoc, on_delete=models.SET_NULL, null=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Đơn Thuốc"
        verbose_name_plural = "Đơn Thuốc"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(DonThuoc, self).save(*args, **kwargs)

class LichSuTrangThaiDonThuoc(models.Model):
    don_thuoc = models.ForeignKey(DonThuoc, on_delete=models.CASCADE)
    trang_thai_don_thuoc = models.ForeignKey(TrangThaiDonThuoc, on_delete=models.CASCADE)
    chi_tiet_trang_thai = models.TextField()

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class KeDonThuoc(models.Model):
    don_thuoc = models.ForeignKey(DonThuoc, on_delete=models.PROTECT, null=True, related_name="ke_don")
    # bac_si_lam_sang = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="bac_si_lam_sang")
    # benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="don_thuoc_benh_nhan")
    thuoc = models.ForeignKey(Thuoc, on_delete=models.SET(get_sentinel_thuoc))
    cach_dung = models.TextField()
    so_luong = models.PositiveIntegerField()
    ghi_chu = models.TextField()
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Kê Đơn Thuốc"
        verbose_name_plural = "Kê Đơn Thuốc"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(KeDonThuoc, self).save(*args, **kwargs)

    def gia_thuoc_theo_bao_hiem(self):
        gia_ban = self.thuoc.gia_thuoc.gia
        if self.bao_hiem:    
            tong_tien = gia_ban * decimal.Decimal((1 - (self.thuoc.bao_hiem_thuoc.muc_bao_hiem / 100))) * self.so_luong
        else: 
            tong_tien = gia_ban * self.so_luong
        return tong_tien

    def gia_ban(self):
        gia_ban = self.thuoc.gia_thuoc.gia
        tong_tien = gia_ban * self.so_luong
        return tong_tien

class ThuocLog(models.Model):

    """ 
        IN: In operation happens in real scenario is when items are added to the stock
        OUT: Out operation is used to keep track of why the item is being removed from the stock(sales, return to vendors, etc.)
    """

    IN = "I"
    OUT = "O"
    OPERATIONS = (
        (IN, "In"),
        (OUT, "Out"),
    )
    thuoc = models.ForeignKey(Thuoc, on_delete=models.CASCADE, related_name="thuoc_logs", verbose_name="Thuốc")
    ngay = models.DateTimeField(verbose_name="Ngày giờ")
    quy_trinh = models.CharField(max_length=1, choices=OPERATIONS, verbose_name="Quy trình")
    so_luong = models.IntegerField(default=0, verbose_name="Số lượng")

    class Meta:
        verbose_name = "Thuốc Log"
        verbose_name_plural = "Thuốc Log"

    def __str__(self):
        return self.thuoc.ten_thuoc + ' --> ' + self.quy_trinh

class ChiTietThuoc(models.Model):
    # https://www.drugs.com/article/pharmaceutical-salts.html

        # Theo Drugs.com, các dạng muối phổ biến nhất trong dược phẩm, theo đơn đặt hàng và các sản phẩm ví dụ, là:
        # 1. Hydrochloride (Cetirizine & Benadryl)
        # 2. Sodium (saline)
        # 3. Sulfate (Garamycin, Septopa, & Epsom)
        # 4. Acetate (Lithium)
        # 5. Phosphate/diphosphate (Visicol)
        # 6. Chloride (Bisacodyl)
        # 7. Potassium (Klor-Con & Gen-K)
        # 8. Maleate (Enalapril)
        # 9. Calcium (Caltrate & Tums)
        # 10. Citrate (Bicitra & Cytra-K)
        # 11. Mesylate (Pexeva & Cogentin)
        # 12. Nitrate (Dilatrate & ISMO)
        # 13. Tartrate (Lopressor & Zolpidem)
        # 14. Aluminum (Maalox & Amphojel)
        # 15. Gluconate (Ferrlecit)
 
    # lý do tại sao có bảng Thành phần Thuốc là vì thuốc
     # thường được gọi bằng cả "tên thuốc gốc" và "tên muối" của chúng
     # Một ví dụ là cách tốt nhất để giải thích câu hỏi này.
     # Phiên bản không kê đơn (không kê đơn hoặc OTC) của omeprazole theo toa (Prilosec) là omeprazole magie (Prilosec OTC).
     # Prilosec OTC là muối magiê của omeprazole ở dạng viên nang phóng thích chậm.

    id = models.AutoField(primary_key=True)
    id_thuoc = models.ForeignKey(Thuoc, on_delete=models.CASCADE, verbose_name="Thuốc")
    ten_muoi = models.CharField(max_length=255, verbose_name="Tên thuốc con")
    ham_luong = models.CharField(max_length=255, verbose_name="Hàm lượng")
    mo_ta = models.CharField(max_length=255, verbose_name="Mô tả")
    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Chi Tiết Thuốc'
        verbose_name_plural = 'Chi Tiết Thuốc'