from django.contrib import admin
from .models import BaoHiem, ChuoiKham, DichVuKham, FileKetQua, FileKetQuaChuyenKhoa, FileKetQuaTongQuat, GiaDichVu, KetQuaChuyenKhoa, KetQuaTongQuat, LichHenKham, LichSuChuoiKham, PhanKhoaKham, PhongChucNang, ProfilePhongChucNang, TrangThaiChuoiKham, TrangThaiKhoaKham, TrangThaiLichHen, User

# admin.site.register(Profile)
admin.site.register(User)
admin.site.register(PhongChucNang)
admin.site.register(LichHenKham)
admin.site.register(TrangThaiLichHen)
admin.site.register(ProfilePhongChucNang)
admin.site.register(PhanKhoaKham)
admin.site.register(ChuoiKham)
admin.site.register(KetQuaTongQuat)
admin.site.register(KetQuaChuyenKhoa)
admin.site.register(FileKetQua)
admin.site.register(DichVuKham)
admin.site.register(GiaDichVu)
admin.site.register(BaoHiem)
admin.site.register(TrangThaiChuoiKham)
admin.site.register(TrangThaiKhoaKham)
admin.site.register(FileKetQuaTongQuat)
admin.site.register(FileKetQuaChuyenKhoa)
admin.site.register(LichSuChuoiKham)
# Register your models here.
