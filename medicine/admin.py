from medicine.models import BaoHiemThuoc, ChiTietThuoc, CongTy, DonThuoc, GiaThuoc, KeDonThuoc, NhomThau, Thuoc, ThuocLog, TrangThaiDonThuoc
from django.contrib import admin


admin.site.register(Thuoc)
admin.site.register(DonThuoc)
admin.site.register(TrangThaiDonThuoc)
admin.site.register(KeDonThuoc)
admin.site.register(ThuocLog)
admin.site.register(ChiTietThuoc)
admin.site.register(CongTy)
admin.site.register(GiaThuoc)
admin.site.register(BaoHiemThuoc)
admin.site.register(NhomThau)