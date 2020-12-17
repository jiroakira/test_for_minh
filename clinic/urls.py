from collections import namedtuple
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.db.models import base
from django.views.generic import RedirectView
from medicine.api import ThuocViewSet, CongTyViewSet
from os import name
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from .api import (
    ChuoiKhamGanNhat, ChuoiKhamNguoiDung, ChuoiKhamViewSet, 
    DangKiAPI, DangKiLichHen, DanhSachBenhNhan, DanhSachBenhNhanTheoPhong, DanhSachBenhNhanTheoPhongChucNang, DanhSachChuoiKhamBenhNhan, DanhSachDichVuKhamTheoPhong, DanhSachDichVuTheoPhongChucNang, DanhSachDoanhThuDichVu, DanhSachDoanhThuThuoc, DanhSachDonThuocBenhNhan, DanhSachHoaDonDichVu, DanhSachHoaDonThuoc, DanhSachKhamTrongNgay, DanhSachLichHenTheoBenhNhan, DanhSachPhongChucNang, DanhSachThanhToanLamSang, DanhSachThuocBenhNhan, DanhSachThuocTheoCongTy, DieuPhoiPhongChucNangView, FileKetQuaViewSet, KetQuaChuoiKhamBenhNhan, 
    LichHenKhamViewSet, ListNguoiDungDangKiKham, PhanKhoaKhamBenhNhan, PhongChucNangTheoDichVu, SetChoThanhToan, SetXacNhanKham, TatCaLichHenBenhNhan, ThongTinBenhNhanTheoMa, ThongTinPhongChucNang, UserInfor, 
    UserViewSet, 
    DichVuKhamViewSet,
    PhongChucNangViewSet
)
from .views import BatDauChuoiKhamToggle, KetThucChuoiKhamToggle, LoginView, ThanhToanHoaDonDichVuToggle, add_lich_hen, bat_dau_chuoi_kham, cap_nhat_thong_tin_benh_nhan, cap_nhat_user, chinh_sua_nguon_cung, chinh_sua_phong_chuc_nang, chinh_sua_thuoc, chinh_sua_thuoc_phong_thuoc, combine_pcn_dich_vu, create_dich_vu, create_user, danh_sach_bai_dang, danh_sach_benh_nhan, danh_sach_benh_nhan_cho, danh_sach_dich_vu_kham, danh_sach_kham, danh_sach_phong_chuc_nang, danh_sach_thuoc, danh_sach_thuoc_phong_tai_chinh, doanh_thu_phong_kham, don_thuoc, dung_kham, dung_kham_chuyen_khoa, files_upload_view, hoa_don_dich_vu, hoa_don_thuoc, import_dich_vu_excel, import_thuoc_excel, index, login, phan_khoa_kham, phong_chuyen_khoa, phong_tai_chinh_danh_sach_cho, phong_thuoc_danh_sach_cho, store_cong_ty, store_ke_don, store_phan_khoa, store_thanh_toan_lam_sang, them_dich_vu_kham, them_dich_vu_kham_excel, them_phong_chuc_nang, them_thuoc_excel, update_benh_nhan, update_dich_vu_kham, update_nguon_cung, update_phong_chuc_nang, update_thuoc, update_thuoc_phong_thuoc, update_user, upload_files_chuyen_khoa, upload_files_lam_sang, upload_view, them_moi_thuoc_phong_tai_chinh, create_thuoc, cong_ty, update_lich_hen, danh_sach_lich_hen, store_update_lich_hen, ThanhToanHoaDonThuocToggle, thanh_toan_hoa_don_thuoc, them_thuoc_phong_tai_chinh, upload_view_lam_sang, xoa_lich_hen

from medicine.views import ke_don_thuoc_view
from clinic.views import loginUser

router = routers.DefaultRouter()
router.register('api/nguoi_dung', UserViewSet, basename="users")
router.register('api/dich_vu', DichVuKhamViewSet, basename="dich_vu_kham")
router.register('api/phong_chuc_nang', PhongChucNangViewSet, basename="phong_chuc_nang")
router.register('api/lich_kham', LichHenKhamViewSet, basename="lich_kham")
router.register('api/chuoi_kham', ChuoiKhamViewSet, basename="chuoi_kham")
router.register('api/danh_sach_thuoc', ThuocViewSet, basename="thuoc"),
router.register('api/cong_ty', CongTyViewSet, basename="cong_ty")

# ajax_router = routers.DefaultRouter()
# ajax_router.register('', FileKetQuaViewSet, basename="upload")

nguoi_dung = UserViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
    }
)

dich_vu = DichVuKhamViewSet.as_view(
    {   
        'post': 'create',
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

them_thuoc = ThuocViewSet.as_view(
    {
        'post': 'create'
    }
)

phong_chuc_nang = PhongChucNangViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

lich_kham = LichHenKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

chuoi_kham = ChuoiKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

urlpatterns = [
    # path('', include(router.urls)),

    # * API
    path('api/nguoi_dung/<int:pk>/', nguoi_dung, name='nguoi_dung'),
    path('api/create/dich_vu/', create_dich_vu, name='create_dich_vu'),
    path('api/dich_vu/<int:pk>/', dich_vu, name='dich_vu'),
    path('api/phong_chuc_nang/<int:pk>/', phong_chuc_nang, name='phong_chuc_nang'),

    path('api/them_thuoc/', create_thuoc, name="them_thuoc_api"),
    # path('api/dieu_phoi/phong_chuc_nang/<int:pk>/', DieuPhoiPhongChucNangView.as_view(), name='dieu_phoi'),
    path('api/lich_kham<int:pk>/', lich_kham, name='lich_kham'),
    path('api/chuoi_kham/<int:pk>/', chuoi_kham, name='chuoi_kham'),
    path('api/danh_sach_lich_hen/', ListNguoiDungDangKiKham.as_view(), name='danh_sach_lich_hen'),
    path('api/danh_sach_chuoi_kham/', ChuoiKhamNguoiDung.as_view(), name='danh_sach_chuoi_kham_nguoi_dung'),
    path('api/danh_sach_benh_nhan_theo_phong/', DanhSachBenhNhanTheoPhong.as_view(), name='danh_sach_benh_nhan_theo_phong'),
    path('api/dich_vu_kham/phong_chuc_nang/', PhongChucNangTheoDichVu.as_view(), name='phong_chuc_nang_theo_dich_vu'),
    path('api/thong_tin_phong_chuc_nang/', ThongTinPhongChucNang.as_view(), name='thong_tin_phong_chuc_nang'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang'),
    path('api/danh_sach_thuoc_theo_cong_ty/', DanhSachThuocTheoCongTy.as_view(), name='danh_sach_thuoc_theo_cong_ty'),
    path('api/danh_sach_dich_vu_kham_theo_phong/', DanhSachDichVuKhamTheoPhong.as_view(), name='danh_sach_dich_vu_kham_theo_phong'),
    path('api/danh_sach_dich_vu_theo_phong_chuc_nang/', DanhSachDichVuTheoPhongChucNang.as_view(), name='danh_sach_dich_vu_kham_theo_phong_chuc_nang'),
    # path('api/ket_qua_chuoi_kham/', KetQuaChuoiKhamBenhNhan.as_view(), name="ket_qua_chuoi_kham"),

    # path('upload/', include(ajax_router.urls)),
    path('api/danh_sach_thanh_toan/', DanhSachHoaDonDichVu.as_view(), name='danh_sach_thanh_toan'),
    path('api/danh_sach_hoa_don_thuoc/', DanhSachHoaDonThuoc.as_view(), name='danh_sach_hoa_don_thuoc'),
    path('api/danh_sach_lam_sang/', DanhSachThanhToanLamSang.as_view(), name='danh_sach_lam_sang'),
    path('api/danh_sach_kham_trong_ngay/', DanhSachKhamTrongNgay.as_view(), name='danh_sach_kham_trong_ngay'),
    path('api/thanh_toan_don_thuoc/', ThanhToanHoaDonThuocToggle.as_view(), name='thanh_toan_don_thuoc_api'),
    path('api/thanh_toan_hoa_don_dich_vu/', ThanhToanHoaDonDichVuToggle.as_view(), name='thanh_toan_hoa_don_dich_vu_api'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang_api'),
    path('api/danh_sach_benh_nhan/', DanhSachBenhNhan.as_view(), name='danh_sach_benh_nhan'),
    path('api/danh_sach_benh_nhan_theo_thoi_gian/', DanhSachLichHenTheoBenhNhan.as_view(), name='danh_sach_benh_nhan_theo_thoi_gian'),
    path('api/thong_tin_benh_nhan_theo_ma/', ThongTinBenhNhanTheoMa.as_view(), name='thong_tin_benh_nhan_thao_ma'),

    path('api/danh_sach_phan_khoa/', PhanKhoaKhamBenhNhan.as_view(), name='danh_sach_phan_khoa'),
    path('api/benh_nhan/danh_sach_don_thuoc/', DanhSachDonThuocBenhNhan.as_view(), name='danh_sach_don_thuoc_benh_nhan'),
    path('api/benh_nhan/don_thuoc/', DanhSachThuocBenhNhan.as_view(), name='danh_sach_thuoc_benh_nhan'),
    path('api/benh_nhan/tat_ca_lich_hen/', TatCaLichHenBenhNhan.as_view(), name='tat_ca_lich_hen'),
    path('api/benh_nhan/chuoi_kham_gan_nhat/', ChuoiKhamGanNhat.as_view(), name='chuoi_kham_gan_nhat'),
    path('api/benh_nhan/danh_sach_chuoi_kham/', DanhSachChuoiKhamBenhNhan.as_view(), name='danh_sach_chuoi_kham_benh_nhan'),
    path('api/benh_nhan/chuoi_kham/ket_qua/', KetQuaChuoiKhamBenhNhan.as_view(), name='ket_qua_chuoi_kham_benh_nhan'),
    path('api/banh_nhan/dang_ki_lich_hen/', DangKiLichHen.as_view(), name='dang_ki_lich_hen'),
    path('api/benh_nhan/thong_tin/', UserInfor.as_view(), name='thong_tin_benh_nhan'),

    path('api/danh_sach_benh_nhan_theo_phong_chuc_nang/', DanhSachBenhNhanTheoPhongChucNang.as_view(), name="danh_sach_benh_nhan_theo_phong_chuc_nang"),
    path('api/bat_dau_chuoi_kham/', BatDauChuoiKhamToggle.as_view(), name='bat_dau_chuoi_kham_api'),
    path('api/ket_thuc_chuoi_kham/', KetThucChuoiKhamToggle.as_view(), name='ket_thuc_chuoi_kham_api'),
    path('api/danh_sach_doanh_thu_dich_vu/', DanhSachDoanhThuDichVu.as_view(), name='danh_sach_doanh_thu_dich_vu'),
    path('api/danh_sach_doanh_thu_thuoc/', DanhSachDoanhThuThuoc.as_view(), name='danh_sach_daonh_thu_thuoc'),
    # * VIEW
    path('', RedirectView.as_view(url="index/"), name='home'),
    path('index/', index, name="index"),
    path('danh_sach_benh_nhan/', danh_sach_benh_nhan, name='danh_sach_benh_nhan'),
    path('danh_sach_benh_nhan/<int:id>/cap_nhat_thong_tin_benh_nhan', update_benh_nhan, name="update_benh_nhan"),
    path('cap_nhat_thong_tin_benh_nhan/', cap_nhat_thong_tin_benh_nhan, name="cap_nhat_thong_tin_benh_nhan"),
    
    path('bac_si_lam_sang/danh_sach_benh_nhan_cho/', danh_sach_benh_nhan_cho, name='danh_sach_benh_nhan_cho'),
    path('dang_nhap/', LoginView.as_view(), name='dang_nhap'),
    path('dang_ki/', create_user, name="dang_ki_nguoi_dung"),
    path('phong_chuyen_khoa/', phong_chuyen_khoa, name='phong_chuyen_khoa'),
    path('phong_chuyen_khoa/benh_nhan/<int:id>/upload/', upload_view, name='upload_ket_qua_chuyen_khoa'),
    path('danh_sach_benh_nhan_cho/phan_khoa_kham/<int:id_lich_hen>/', phan_khoa_kham, name='phan_khoa_kham'),
    path('bac_si_lam_sang/ket_qua_kham/', danh_sach_kham, name='danh_sach_kham'),
    path('bac_si_lam_sang/benh_nhan/<int:id>/upload/', upload_view_lam_sang, name='upload_ket_qua_lam_sang'),
    path('danh_sach_kham/ke_don_thuoc/<int:user_id>/', ke_don_thuoc_view, name='ke_don_thuoc'),
    # path('test/', testView, name="test"),
    path('store_phan_khoa_kham/', store_phan_khoa, name='store_phan_khoa'),
    path('store_ke_don/', store_ke_don, name='store_ke_don'),
    path('ke_don_thuoc/', ke_don_thuoc_view, name='ke_don_thuoc'),
    path('upload_files/', files_upload_view, name='upload_files'),
    # path('upload/<int:id>/', upload_view, name='upload'),
    path('upload_files_chuyen_khoa/', upload_files_chuyen_khoa, name="upload_files_chuyen_khoa"),
    path('upload_files_lam_sang/', upload_files_lam_sang, name='upload_files_lam_sang'),
    path('store_cong_ty/', store_cong_ty, name='store_cong_ty'),

    path('danh_sach_lich_hen/', danh_sach_lich_hen, name='danh_sach_lich_hen'),
    path('danh_sach_lich_hen/lich_hen/<int:id>/', update_lich_hen, name='update_lich_hen'),
    path('store_update_lich_hen', store_update_lich_hen, name="store_update_lich_hen"),
    path('xoa_lich_hen/', xoa_lich_hen, name="xoa_lich_hen"),
    path('set_cho_thanh_toan/', SetChoThanhToan.as_view(), name="set_cho_thanh_toan"),
    path('set_xac_nhan_kham/', SetXacNhanKham.as_view(), name="set_xac_nhan_kham"),

    path('bat_dau_chuoi_kham/<int:id>/', bat_dau_chuoi_kham, name='bat_dau_chuoi_kham'),
    path('bac_si_lam_sang/dung_kham_dot_xuat/', dung_kham, name='dung_kham'),
    path('bac_si_chuyen_khoa/dung_kham/', dung_kham_chuyen_khoa, name='dung_kham_chuyen_khoa'),

    path('phong_tai_chinh/', phong_tai_chinh_danh_sach_cho, name='phong_tai_chinh'),
    path('phong_thuoc/', phong_thuoc_danh_sach_cho, name='phong_thuoc'),
    path('phong_tai_chinh/hoa_don_dich_vu/<int:id_chuoi_kham>/', hoa_don_dich_vu, name='hoa_don_dich_vu'),
    path('phong_tai_chinh/hoa_don_thuoc/<int:id_don_thuoc>/', hoa_don_thuoc, name='hoa_don_thuoc'),
    path('phong_tai_chinh/danh_sach_thuoc/', danh_sach_thuoc_phong_tai_chinh, name='danh_sach_thuoc_phong_tai_chinh'),
    path('phong_tai_chinh/hoa_don_thuoc/thanh_toan/', thanh_toan_hoa_don_thuoc, name='thanh_toan_hoa_don_thuoc'),
    path('phong_tai_chinh/them_thuoc/', them_thuoc_phong_tai_chinh, name='them_thuoc_phong_tai_chinh'),
    path('phong_thuoc/don_thuoc/<int:id_don_thuoc>/', don_thuoc, name='don_thuoc'),
    path('phong_thuoc/danh_sach_thuoc/', danh_sach_thuoc, name='danh_sach_thuoc_phong_thuoc'),
    path('phong_tai_chinh/them_moi_thuoc/', them_moi_thuoc_phong_tai_chinh, name="phong_tai_chinh_them_moi_thuoc"),
    path('nguon_cung/', cong_ty, name="nguon_cung"),
    path('nguon_cung/<int:id>/chinh_sua/', update_nguon_cung, name="update_nguon_cung"),
    path('chinh_sua/', chinh_sua_nguon_cung, name="chinh_sua"),
    path('danh_sach_phong_chuc_nang/', danh_sach_phong_chuc_nang, name="danh_sach_phong_chuc_nang"),
    path('them_phong_chuc_nang/', them_phong_chuc_nang, name="them_phong_chuc_nang"),
    # path('danh_sach_phong_chuc_nang/', danh_sach_phong_chuc_nang, name),
    path('danh_sach_dich_vu_kham/', danh_sach_dich_vu_kham, name="danh_sach_dich_vu_kham"),
    path('danh_sach_phong_chuc_nang/<int:id>/chinh_sua_phong_chuc_nang', update_phong_chuc_nang, name="update_phong_chuc_nang"),
    path('danh_sach_dich_vu_kham/<int:id>/chinh_sua_dich_vu_kham', update_dich_vu_kham, name="update_dich_vu_kham"),
    path('chinh_sua_phong_chuc_nang/', chinh_sua_phong_chuc_nang, name="chinh_sua_phong_chuc_nang"),
    path('cap_nhat_thong_tin/<int:id>', update_user, name="update_user"),
    path('cap_nhat_user/', cap_nhat_user, name="cap_nhat_user"),
    path('phong_tai_chinh/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc, name="cap_nhat_thuoc"),
    path('update_thuoc/', update_thuoc, name="update_thuoc"),
    path('phong_thuoc/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc_phong_thuoc, name="cap_nhat_thuoc_phong_thuoc"),
    path('update_thuoc_phong_thuoc/', update_thuoc_phong_thuoc, name="update_thuoc_phong_thuoc"),
    path('phong_tai_chinh/doanh_thu_phong_kham/', doanh_thu_phong_kham, name="doanh_thu_phong_kham"),
    path('them_dich_vu_kham_excel/', them_dich_vu_kham_excel, name='them_dich_vu_kham_excel'),
    path('store_dich_vu_excel/', import_dich_vu_excel, name="import_dich_vu_excel"),
    path('them_thuoc_excel/', them_thuoc_excel, name="them_thuoc_excel"),
    path('import_thuoc_excel/', import_thuoc_excel, name="import_thuoc_excel"),
    path('them_dich_vu_kham/', them_dich_vu_kham, name="them_dich_vu_kham"),
    path('tao_lich_hen/', add_lich_hen, name='add_lich_hen'),
    path('danh_sach_bai_dang/', danh_sach_bai_dang, name="danh_sach_bai_dang"),
    path('thanh_toan_lam_sang/', store_thanh_toan_lam_sang, name="store_thanh_toan_lam_sang"),
 
    path('gan_dich_vu_voi_phong_chuc_nang', combine_pcn_dich_vu, name='phong_chuc_nang_dich_vu'),

    path('login/', login, name='login'),
    path('loginUser/', loginUser, name='loginUser'),
    
    path('logout/',auth_views.LogoutView.as_view(next_page='dang_nhap'),name='logout'),
]