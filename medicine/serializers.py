from django.db.models import fields
from clinic.models import file_url
from rest_framework import serializers
from medicine.models import CongTy, KeDonThuoc, NhomThau, Thuoc

class CongTySerializer(serializers.ModelSerializer):
    class Meta:
        model = CongTy
        fields = "__all__"


class NhomThauSerializer(serializers.ModelSerializer):

    class Meta:
        model = NhomThau
        fields = "__all__"
class ThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thuoc
        fields = "__all__"
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['cong_ty'] = CongTySerializer(instance.cong_ty).data
        response['nhom_thau'] = NhomThauSerializer(instance.nhom_thau).data
        return response

# class KeDonThuocSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = KeDonThuoc
#         fields = '__all__'

class ThuocSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Thuoc
        fields = ('id', 'ten_thuoc', 'duong_dung', 'don_vi_tinh')

class KeDonThuocSerializer(serializers.ModelSerializer):
    thuoc = ThuocSerializerSimple()
    class Meta:
        model = KeDonThuoc
        fields = ('id', 'thuoc', 'so_luong', 'cach_dung', 'ghi_chu')