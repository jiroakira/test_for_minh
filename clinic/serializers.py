from finance.models import HoaDonChuoiKham, HoaDonThuoc
from medicine.serializers import CongTySerializer, ThuocSerializer
# from finance.serializers import HoaDonChuoiKhamSerializer, HoaDonThuocSerializer
from os import set_inheritable
from django.http.request import validate_host
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DichVuKham, FileKetQua, FileKetQuaChuyenKhoa, KetQuaChuyenKhoa, KetQuaTongQuat, 
    LichHenKham, PhanKhoaKham, 
    PhongChucNang, 
    ProfilePhongChucNang, TrangThaiChuoiKham, TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    ChuoiKham
)
from medicine.models import DonThuoc

User = get_user_model()

class ChildUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'so_dien_thoai', 'ho_ten', 'email', 'cmnd_cccd', 'chuc_nang') 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'so_dien_thoai', 'ho_ten', 'email', 'cmnd_cccd', 'dia_chi', 'ngay_sinh', 'gioi_tinh')
        extra_kwargs = {'password': {'write_only': True}}

    # TODO create and update child instance of user
    # TODO review again

class UserLoginSerializer(serializers.Serializer):
    so_dien_thoai = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class DangKiSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('so_dien_thoai', 'password', 'ho_ten')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(ho_ten = validated_data['ho_ten'], so_dien_thoai = validated_data['so_dien_thoai'], password = validated_data['password'])
        return user

class DichVuKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DichVuKham
        fields = '__all__'

    # def create(self, validated_data):
    #     ten_dich_vu = validated_data.get('ten_dich_vu')
    #     dich_vu = DichVuKham.objects.get_or_create(ten_dich_vu = ten_dich_vu)[0]
    #     return dich_vu

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['bac_si_phu_trach'] = UserSerializer(instance.bac_si_phu_trach).data
        return response

class PhongChucNangSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhongChucNang
        fields = '__all__'

    def create(self, validated_data):
        ten_phong_chuc_nang = validated_data.get('ten_phong_chuc_nang')
        phong_chuc_nang = PhongChucNang.objects.get_or_create(ten_phong_chuc_nang = ten_phong_chuc_nang)[0]
        return phong_chuc_nang

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['dich_vu_kham'] = DichVuKhamSerializer(instance.dich_vu_kham).data
        return response

class ProfilePhongChucNangSerializer(serializers.ModelSerializer):
    phong_chuc_nang = PhongChucNangSerializer()
    class Meta:
        model = ProfilePhongChucNang
        fields = '__all__'

class LichHenKhamSerializer(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    nguoi_phu_trach = UserSerializer()
    class Meta:
        model = LichHenKham
        fields = '__all__'

    def create(self, validated_data):
        benh_nhan = validated_data.get('benh_nhan')
        ngay_hen = validated_data.get('ngay_hen')
        thoi_gian_bat_dau = validated_data.get('thoi_gian_bat_dau')
        lich_hen = LichHenKham.objects.get_or_create(
            benh_nhan=benh_nhan,
            ngay_hen=ngay_hen,
            thoi_gian_bat_dau=thoi_gian_bat_dau
        )
        return lich_hen
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['actions'] = ''
        return response

class TrangThaiLichHenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiLichHen
        fields = '__all__'

class TrangThaiKhoaKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiKhoaKham
        fields = '__all__'

class TrangThaiChuoiKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiChuoiKham
        fields = '__all__'


class ChuoiKhamSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()
    class Meta:
        model = ChuoiKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'benh_nhan', 'bac_si_dam_nhan', 'trang_thai')

class ChuoiKhamPhanKhoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChuoiKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'benh_nhan', 'bac_si_dam_nhan', 'trang_thai')
 
class PhanKhoaKhamSerializer(serializers.ModelSerializer):
    chuoi_kham = ChuoiKhamPhanKhoaSerializer()
    benh_nhan = UserSerializer()
    bac_si_lam_sang = UserSerializer()
    dich_vu_kham = DichVuKhamSerializer()
    class Meta:
        model = PhanKhoaKham
        fields = ('id','chuoi_kham', 'benh_nhan', 'bac_si_lam_sang', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'dich_vu_kham')

class FileKetQuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileKetQua
        fields = ('id', 'file')

class FileKetQuaChuyenKhoaSerializer(serializers.ModelSerializer):
    file = FileKetQuaSerializer()
    class Meta:
        model = FileKetQuaChuyenKhoa
        fields = ('id', 'file')

class KetQuaChuyenKhoaSerializer(serializers.ModelSerializer):
    file_chuyen_khoa = FileKetQuaChuyenKhoaSerializer(many=True, source='file_ket_qua_chuyen_khoa')
    class Meta:
        model = KetQuaChuyenKhoa
        fields = ('id', 'ma_ket_qua', 'mo_ta', 'ket_luan', 'file_chuyen_khoa')

class KetQuaTongQuatSerializer(serializers.ModelSerializer):
    kq_chuyen_khoa = KetQuaChuyenKhoaSerializer(many=True, source='ket_qua_chuyen_khoa')
    class Meta:
        model = KetQuaTongQuat
        fields = ('id', 'ma_ket_qua', 'mo_ta', 'ket_luan', 'kq_chuyen_khoa')

class ChuoiKhamSerializer(serializers.ModelSerializer):
    phan_khoa_kham = PhanKhoaKhamSerializer(many=True)
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()
    class Meta:
        model = ChuoiKham
        fields = '__all__'
 
    def create(self, validated_data):
        pass
 
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['actions'] = ''
        return response

class FileKetQuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileKetQua
        fields = ('id', 'file')

class HoaDonChuoiKhamSerializer(serializers.ModelSerializer):
    chuoi_kham = ChuoiKhamSerializer()
    class Meta:
        model = HoaDonChuoiKham
        fields = '__all__'
        
class HoaDonThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDonThuoc
        fields = '__all__'
class HoaDonChuoiKhamSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()  
    hoa_don = HoaDonChuoiKhamSerializer(read_only=True, source = 'hoa_don_dich_vu')
    class Meta:
        model = ChuoiKham
        depth = 1
        fields = (
            'id', 
            'benh_nhan', 
            'bac_si_dam_nhan',
            'trang_thai',
            'hoa_don',
            'thoi_gian_tao',
        )

class HoaDonThuocSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_ke_don = UserSerializer()
    don_thuoc = HoaDonThuocSerializer(read_only=True, source = 'hoa_don_thuoc')
    class Meta:
        model = DonThuoc
        fields = (
            'id',
            'benh_nhan', 
            'bac_si_ke_don',
            'trang_thai',
            'don_thuoc',
            'thoi_gian_tao',
        )


class PhanKhoaKhamDichVuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhanKhoaKham
        fields = ('id', 'chuoi_kham', 'benh_nhan', 'bac_si_lam_sang', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'dich_vu_kham')

class PhongChucNangSerializer(serializers.ModelSerializer):
    dich_vu_kham = DichVuKhamSerializer()
    danh_sach_benh_nhan = PhanKhoaKhamDichVuSerializer(source='danh_sach_benh_nhan_theo_dich_vu_kham', many=
    True)
    class Meta:
        model = PhongChucNang
        fields = ('id', 'dich_vu_kham', 'ten_phong_chuc_nang', 'danh_sach_benh_nhan')

class PhongChucNangSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = PhongChucNang
        fields = "__all__"

class DichVuKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DichVuKham
        fields = '__all__'

# class DanhSachPhongChucNang(APIView);
# class DanhSachKetQuaChuyenKhoa(APIView):
#     ket_qua_chuyen_khoa = KetQuaChuyenKhoaSerializer