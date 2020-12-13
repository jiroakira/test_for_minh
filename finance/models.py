from django.db import models
from django.utils import timezone

class HoaDonThuoc(models.Model):
    # benh_nhan = models.ForeignKey(NguoiDung, on_delete=models.SET(get_sentinel_user))
    """ 
    * Bảng hóa đơn thuốc sẽ lưu trữ lại hóa đơn của tất cả người dùng
    
    @field chuoi_kham: mối quan hệ 1-1 với Chuỗi Khám, vì một chuỗi khám sẽ chỉ có một hóa đơn
    @field ma_hoa_don: mã hóa đơn này sẽ do bác sĩ tự quy định, bác sĩ có thể quy định mã hóa đơn này theo người bệnh và thời gian họ khám để dễ dàng phân biệt
    @field tong_tien: tổng số tiền của các thuốc mà bệnh nhân đã được kê đơn
    @field thoi_gian_tao: thời gian hóa đơn được tạo
    @field thoi_gian_cap_nhat: thời gian hóa đơn được cập nhật
    """
    don_thuoc = models.OneToOneField("medicine.DonThuoc", on_delete=models.SET_NULL, null=True, related_name='hoa_don_thuoc')
    ma_hoa_don = models.CharField(max_length=255, unique=True, null=True, blank=True)
    tong_tien = models.DecimalField(decimal_places=3, max_digits=10, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonThuoc, self).save(*args, **kwargs)

class HoaDonChuoiKham(models.Model):
    """ 
    * Bảng hóa đơn khám sẽ lưu trữ lại hóa đơn sau khi sử dụng các dịch vụ khám của tất cả người dùng 

    @field chuoi_kham: mối quan hệ 1-1 với Chuỗi Khám, vì một chuỗi khám sẽ chỉ có một hóa đơn
    @field ma_hoa_don: mã hóa đơn này sẽ do bác sĩ tự quy định, bác sĩ có thể quy định mã hóa đơn này theo người bệnh và thời gian họ khám để dễ dàng phân biệt
    @field tong_tien: tổng số tiền của các dịch vụ khám mà bệnh nhân đã khám
    @field thoi_gian_tao: thời gian hóa đơn được tạo
    @field thoi_gian_cap_nhat : thời gian hóa đơn được cập nhật
    """

    chuoi_kham = models.OneToOneField("clinic.ChuoiKham", on_delete=models.SET_NULL, null=True, related_name='hoa_don_dich_vu')
    ma_hoa_don = models.CharField(max_length=255, null=True, blank=True, unique=True)
    tong_tien = models.DecimalField(decimal_places=3, max_digits=10, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonChuoiKham, self).save(*args, **kwargs)

    # TODO: trường tổng tiền có trong 2 hóa đơn sẽ được update sau khi bệnh nhân đóng tiền (transaction atomic update)

class HoaDonLamSang(models.Model):
    gia_tien = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    # benh_nhan = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

class HoaDonTong(models.Model):
    benh_nhan = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="hoa_don_tong_nguoi_dung")
    lich_hen = models.ForeignKey("clinic.LichHenKham", on_delete=models.SET_NULL, null=True, blank=True, related_name="hoa_don_lich_hen")
    hoa_don_lam_sang = models.ForeignKey(HoaDonLamSang, on_delete=models.SET_NULL, null=True, blank=True)
    hoa_don_chuoi_kham = models.ForeignKey(HoaDonChuoiKham, on_delete=models.SET_NULL, null=True, blank=True)
    hoa_don_thuoc = models.ForeignKey(HoaDonThuoc, on_delete=models.SET_NULL, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonTong, self).save(*args, **kwargs)