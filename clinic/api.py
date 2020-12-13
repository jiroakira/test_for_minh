
from finance.models import HoaDonChuoiKham, HoaDonThuoc
from finance.serializers import HoaDonChuoiKhamSerializer
from json import dump
import json
from django.db.models.query_utils import select_related_descend

from rest_framework import serializers
# from clinic.views import danh_sach_phong_chuc_nang
from medicine.models import DonThuoc, Thuoc, TrangThaiDonThuoc
from django.db.models import query
from django.http.response import Http404, HttpResponse, JsonResponse
from rest_framework import views
from rest_framework.views import APIView
from clinic.models import DichVuKham, FileKetQua, KetQuaTongQuat, LichHenKham, PhanKhoaKham, PhongChucNang, TrangThaiChuoiKham, TrangThaiKhoaKham, TrangThaiLichHen, ChuoiKham, KetQuaChuyenKhoa
from rest_framework import viewsets
from django.contrib.auth import authenticate, get_user_model
from .serializers import BookLichHenKhamSerializer, DangKiSerializer, DanhSachDonThuocSerializer, DanhSachPhanKhoaSerializer, DichVuKhamSerializer, DonThuocSerializer, FileKetQuaSerializer, HoaDonChuoiKhamSerializerSimple, HoaDonThuocSerializer, HoaDonThuocSerializerSimple, KetQuaTongQuatSerializer, LichHenKhamSerializer, LichHenKhamSerializerSimple, LichHenKhamUserSerializer, PhanKhoaKhamDichVuSerializer, PhanKhoaKhamSerializer, PhongChucNangSerializer, PhongChucNangSerializerSimple, ProfilePhongChucNangSerializer, TrangThaiLichHenSerializer, UserLoginSerializer, UserSerializer, ChuoiKhamSerializer, KetQuaChuyenKhoaSerializer, ChuoiKhamSerializerSimple, UserSerializerSimple
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics, permissions, mixins
from rest_framework.request import Request
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay
from django.db.models import Count, F, Sum, Q
from django.db import models
from medicine.serializers import KeDonThuocSerializer, ThuocSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def list(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True, context={"request": request})

        user_data = serializer.data

        ds_user_moi = []

        for user in user_data:
            child_user = User.objects.filter(parent = user['id'])
            child_user_serializer = UserSerializer(child_user, many=True)
            user['child'] = child_user_serializer.data
            ds_user_moi.append(user)

        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh sach Nguoi dung",
            "data": ds_user_moi,
        }
        return Response(response)

    def create(self, request):
        try:
            user_serializer = UserSerializer(data=request.data, context={"request": request})
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
            response = {
                "error": False,
                "status": status.HTTP_201_CREATED,
                "message" : "Them Nguoi Dung Thanh Cong",
            }
        except:
            response = {
                "error": True,
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Moi Nguoi Dung",
            }

        return Response(response)

    # def retrieve(self, request: Request, pk=None):
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user, context={"request": request})

    #     user_data = serializer.data

    #     return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
    
    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            return Response(self.get_serializer(request.user).data)
        else:
            queryset = User.objects.all()
            user = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = UserSerializer(user, context={"request": request})
            user_data = serializer.data
            return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
        return super().retrieve(request, **kwargs)

    # TODO set quyền cho người dùng, chỉ có admin mới thấy được chi tiết của từng người dùng, còn lại mỗi người dùng chỉ thấy được chi tiết của họ

    def update(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        
        serialzer = UserSerializer(user, data=request.data, context={"request": request})
        serialzer.is_valid()
        serialzer.save()

        # for child_user_data in request.data["parent"]:
        #     print(child_user_data)

        # try:
        #     for child_user_data in request.data["parent"]:
        #         if child_user_data["id"] == 0:
        #             # tao moi 1 tai khoan con

        #             del child_user_data["id"]
        #             child_user_data["parent"] = serialzer.data["id"]
        #             child_user_serializer = UserSerializer(data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
        #         else:
        #             # update tai khoan con
        #             queryset2 = User.objects.all()
        #             child_user = get_object_or_404(queryset2, pk=child_user_data["id"])
        #             del child_user_data["id"]
        #             child_user_serializer = UserSerializer(child_user, data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
            
        #     return Response({"error": True, "message": child_user_serializer.error_messages})
        # except:
        # return Response({"error": True, "message": serialzer.error_messages})
        return Response({"error": False, "status": status.HTTP_200_OK, "message": "Cap Nhat Du Lieu Thanh Cong"})

    # TODO create JWT authentication

class DangNhapAPI(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                so_dien_thoai = serializer.validated_data['so_dien_thoai'],
                password = serializer.validated_data['password']
            )
            u = User.objects.get(so_dien_thoai=serializer.validated_data['so_dien_thoai'])
            user_serializer = UserSerializerSimple(u, context={'request': request})
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    'user_id': u.id,
                    'user_data': user_serializer.data
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response({
                "error_message": "So Dien Thoai Hoac Mat Khau Khong Dung",
                'error_code': 400,
            },status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "error_message": serializer.errors,
            "error_code": 400
        }, status=status.HTTP_400_BAD_REQUEST)

class DangKiAPI(generics.GenericAPIView):
    serializer_class = DangKiSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "status": status.HTTP_201_CREATED,
            "message": "Đăng Kí Tài Khoản Thành Công"
        })

class DichVuKhamViewSet(viewsets.ViewSet):

    def list(self, request):
        phong_chuc_nang = PhongChucNangSerializerSimple()
        dich_vu_kham = DichVuKham.objects.all()
        serializer = DichVuKhamSerializer(dich_vu_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Dich Vu Kham",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = DichVuKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Dich Vu Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Dich Vu Kham"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        serializer = DichVuKhamSerializer(dich_vu_kham, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Dich Vu: {dich_vu_kham.ten_dich_vu}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = DichVuKham.objects.all()
            dich_vu_kham = get_object_or_404(queryset, pk=pk)
            serializer = DichVuKhamSerializer(dich_vu_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Dich Vu",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        dich_vu_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xoa Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong"
        })

class PhongChucNangViewSet(viewsets.ModelViewSet):
    def list(self, request):
        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Phong Chuc Nang",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = PhongChucNangSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Phong Chuc Nang Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Phong Chuc Nang"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        serializer = PhongChucNangSerializer(phong_chuc_nang, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Phong Chuc Nang: {phong_chuc_nang.ten_phong_chuc_nang}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = PhongChucNang.objects.all()
            phong_chuc_nang = get_object_or_404(queryset, pk=pk)
            serializer = PhongChucNangSerializer(phong_chuc_nang, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Phong Chuc Nang {phong_chuc_nang.ten_phong_chuc_nang} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Phong Chuc Nang",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        phong_chuc_nang.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xóa Phòng Chức Năng {phong_chuc_nang.ten_phong_chuc_nang} Thành Công"
        })

class LichHenKhamViewSet(viewsets.ModelViewSet):
    serializer_class = LichHenKhamSerializer

    def list(self, request):
        # trang_thai = TrangThaiLichHen.objects.filter(Q(ten_trang_thai="Thanh Toán Lâm Sàng") | Q(ten_trang_thai = "Chờ Thanh Toán"))
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0] 
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        lich_hen = LichHenKham.objects.filter(trang_thai=trang_thai, thoi_gian_bat_dau__lte=today_end)
        # lich_hen = LichHenKham.objects.filter(trang_thai = trang_thai).annotate(relevance=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then=1),
        #     models.When(thoi_gian_bat_dau__lt=now, then=2),
        #     output_field=models.IntegerField(),
        # )).annotate(
        # timediff=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then= F('thoi_gian_bat_dau') - now),
        #     models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
        #     # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
        #     output_field=models.DurationField(),
        # )).order_by('relevance', 'timediff')
        # upcoming_events = []
        # for lich in lich_hen:
        #     if lich.relevance == 1:
        #         upcoming_events.append(lich)

        serializer = LichHenKhamSerializer(lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Lich Hen Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = LichHenKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Lich Hen"
            }
        return Response(response)

    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            queryset = LichHenKham.objects.filter(benh_nhan=request.user)
            serializer = LichHenKhamSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = LichHenKhamSerializer(lich_hen, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Lich Hen",
                "data": data
            }
            return Response(response)
        return super().retrieve(*args, **kwargs)

    def update(self, request, pk=None):
        try:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = LichHenKhamSerializer(lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = LichHenKham.objects.all()
        lich_hen = get_object_or_404(queryset, pk=pk)
        lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

    # NOTE: khi lễ tân cập nhật lịch hẹn, sẽ tự động cập nhật trường nguoi_phu_trach
    # def perform_update(self, serializer):
    #     serializer.save(nguoi_phu_trach=self.request.user)

class TrangThaiLichHenViewSet(viewsets.ModelViewSet):
    def list(self, request):
        trang_thai_lich_hen = TrangThaiLichHen.objects.all()
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Trang Thai Lich Hen",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = TrangThaiLichHenSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Trang Thai Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Trang Thai Lich Hen"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Lich Hen",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = TrangThaiLichHen.objects.all()
            trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        trang_thai_lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

class ChuoiKhamViewSet(viewsets.ModelViewSet):
    queryset = ChuoiKham.objects.all()
    serializer_class = ChuoiKhamSerializer

    def get_queryset(self):
        if self.action == 'retrieve': 
            return self.queryset.filter(benh_nhan=self.request.user)
        return self.queryset

    def list(self, request):
        chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').all().order_by("-thoi_gian_tao")
        serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Chuoi Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = ChuoiKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Chuoi Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Chuoi Kham"
            }
        return Response(response)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            chuoi_kham = ChuoiKham.objects.filter(benh_nhan=request.user.id)
            serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=kwargs.get('pk'))

            serializer = ChuoiKhamSerializer(chuoi_kham, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Chuoi Kham",
                "data": data
            }
            return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=pk)
            serializer = ChuoiKhamSerializer(chuoi_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Chuoi Kham Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Chuoi Kham"
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = ChuoiKham.objects.all()
        chuoi_kham = get_object_or_404(queryset, pk=pk)
        chuoi_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Chuoi Kham Thanh Cong"
        })

    # TODO chuỗi khám sẽ query theo user, từng user sẽ có 1 list các chuỗi khám
    
    # TODO điều phối khám cho bệnh nhân 

class KetQuaTongQuatViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_tong_quat = KetQuaTongQuat.objects.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Tong Quat",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaTongQuatSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Tong Quat Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Tong Quat"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Tong Quat",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaTongQuat.objects.all()
            ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Tong Quat Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Tong Quat",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        ket_qua_tong_quat.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Tong Quat Thanh Cong"
        })
    
    # TODO kết quả tổng quát sẽ query theo chuỗi khám, mỗi chuỗi khám sẽ có một kết quả tổng quát

class KetQuaChuyenKhoaViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.all()
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Chuyen Khoa",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaChuyenKhoaSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Chuyen Khoa Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Chuyen Khoa"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Chuyen Khoa",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaChuyenKhoa.objects.all()
            ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Chuyen Khoa Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Chuyen Khoa",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        ket_qua_chuyen_khoa.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Chuyen Khoa Thanh Cong"
        })
    
    # TODO kết quả chuyên khoa sẽ query theo kết quả tổng quát, mỗi kết quả tổng quát sẽ có nhiều kết quả chuyên khoa

class DieuPhoiPhongChucNangView(views.APIView):

    def get_object(self, pk):
        try:
            return PhongChucNang.objects.get(pk=pk)
        except PhongChucNang.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        phong_chuc_nang = self.get_object(pk=pk)
        dich_vu_kham = phong_chuc_nang.dich_vu_kham
        chuoi_kham = dich_vu_kham.dich_vu_kham.all()
        serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
        return Response(serializer.data)

class FileKetQuaViewSet(viewsets.ModelViewSet):
    serializer_class = FileKetQuaSerializer
    queryset = FileKetQua.objects.all()


class ListNguoiDungDangKiKham(APIView):
    def get(self, request, format=None):
        queryset = LichHenKham.objects.select_related('benh_nhan').filter(trang_thai=4)
        serializer = LichHenKhamSerializer(queryset, many=True, context={'request': request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "data": serializer.data
        }
        return Response(response)

class ChuoiKhamNguoiDung(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').filter(benh_nhan=user_id)
            serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
            response = {
                "error": False,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response)

class DanhSachThuocTheoCongTy(APIView):
    def get(self, request, format=None):
        id_cong_ty = self.request.query_params.get('id_cong_ty', None)
        if id_cong_ty:
            thuoc = Thuoc.objects.select_related('cong_ty').filter(cong_ty = id_cong_ty)
            serializer = ThuocSerializer(thuoc, many=True, context={"request":request})
            response = {
                "error" : False,
                "status" : status.HTTP_200_OK,
                "data" : serializer.data
            }
            return Response(response)
class DanhSachBenhNhanTheoPhong(APIView):
    def get(self, request, format=None):
        id_phong = self.request.query_params.get('id_phong', None)
        if id_phong:
            phong_chuc_nang = get_object_or_404(PhongChucNang, id=id_phong)
            # dich_vu_kham = 
            chuyen_khoa_kham = phong_chuc_nang.dich_vu_kham
            ds_phan_khoa_by_users = chuyen_khoa_kham.dich_vu_kham.all()
            serializer = PhanKhoaKhamSerializer(ds_phan_khoa_by_users, many=True, context={'request': request})
            response_data = {
                "error": False,
                "status": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            return Response(response_data)
        # return Response({'key': serializer.data}, status=status.HTTP_200_OK)

# TODO Danh sách bệnh nhân theo phòng: nếu trạng thái chuỗi khám và phân khoa khám của bệnh nhân trở thành "Dừng Lại" thì sẽ filter exclude trạng thái "Dừng Lại"

class DanhSachDichVuKhamTheoPhong(APIView):
    def get(self, request, format=None):
        ten_phong_chuc_nang = self.request.query_params.get('ten_phong_chuc_nang')
        phong_chuc_nang = PhongChucNang.objects.filter(ten_phong_chuc_nang=ten_phong_chuc_nang)
        # dich_vu_kham = 
        danh_sach = PhanKhoaKham.objects.filter(dich_vu_kham__phong_chuc_nang_theo_dich_vu__ten_phong_chuc_nang=ten_phong_chuc_nang).distinct()

        serializer = PhanKhoaKhamSerializer(danh_sach, many=True, context={'request': request})
        # serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):
        phong_chuc_nang = PhongChucNang.objects.values('ten_phong_chuc_nang').distinct()
        serializers = PhongChucNangSerializer(phong_chuc_nang, many=True, context = {'request':request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "data": serializers.data
        }
        
        return Response(response)
class PhongChucNangTheoDichVu(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            data_phong = phong_chuc_nang[0]
            profile_phong_chuc_nang = data_phong.profile_phong_chuc_nang
            serializer = ProfilePhongChucNangSerializer(profile_phong_chuc_nang, context={'request': request})
            data = serializer.data
            # print(data)
            response_data = {
                'ten_phong_chuc_nang': data['phong_chuc_nang']['ten_phong_chuc_nang'],
                'so_luong_cho': data['so_luong_cho'],
                'thoi_gian_cho': data['thoi_gian_trung_binh'],
            }

            return Response(response_data)

class DanhSachHoaDonDichVu(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiChuoiKham.objects.filter(trang_thai_chuoi_kham="Chờ Thanh Toán")[0]
        danh_sach_chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').filter(trang_thai=trang_thai, thoi_gian_tao__lt=today_end)
        serializer = HoaDonChuoiKhamSerializerSimple(danh_sach_chuoi_kham, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachHoaDonThuoc(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiDonThuoc.objects.filter(trang_thai="Chờ Thanh Toán")[0]
        danh_sach_don_thuoc = DonThuoc.objects.select_related('benh_nhan').filter(trang_thai=trang_thai, thoi_gian_tao__lt=today_end)
        serializer = HoaDonThuocSerializerSimple(danh_sach_don_thuoc, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachThanhToanLamSang(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiLichHen.objects.filter(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]
        danh_sach_lam_sang = LichHenKham.objects.select_related('benh_nhan').filter(trang_thai = trang_thai, thoi_gian_tao__lt=today_end)
        serializer = LichHenKhamSerializer(danh_sach_lam_sang, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data,
        }
        return Response(response_data)
class ThongTinPhongChucNang(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            if len(phong_chuc_nang) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            trang_thai_cho = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang chờ')[0]
            trang_thai_thuc_hien = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang Thực Hiện')[0]
            ds_benh_nhan = dich_vu.dich_vu_kham.select_related().filter(Q(trang_thai=trang_thai_cho) | Q(trang_thai=trang_thai_thuc_hien))
            ds_benh_nhan_dang_cho = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_cho)
            ds_benh_nhan_dang_thuc_hien = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_thuc_hien)
            if len(ds_benh_nhan) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            so_luong = ds_benh_nhan.count()
            so_luong_cho = ds_benh_nhan_dang_cho.count()
            so_luong_thuc_hien = ds_benh_nhan_dang_thuc_hien.count()
            data_phong = phong_chuc_nang[0]
            open_div = "<div class='text-left'>"
            close_div = "</div>"
            html_ten_phong = f"<span class='head'>Phòng : </span><span>{data_phong.ten_phong_chuc_nang}</span><br/>"
            html_so_luong = f"<span class='head'>Tổng Số Người : </span><span>{so_luong}</span><br/>"
            html_so_luong_dang_cho = f"<span class='head'>Đang Chờ : </span><span>{so_luong_cho}</span><br/>"
            html_so_luong_dang_thuc_hien = f"<span class='head'>Đang Thực Hiện : </span><span>{so_luong_thuc_hien}</span><br/>"
            html = open_div + html_ten_phong + html_so_luong + html_so_luong_dang_cho + html_so_luong_dang_thuc_hien + close_div
            response_data = {
                'status': 200,
                'html': str(html)
            }
            
            return Response(response_data)

class DanhSachKhamTrongNgay(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        # cho_thanh_toan = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Chờ Thanh Toán")
        da_thanh_toan = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham='Đã Thanh Toán')
        # dang_thuc_hien = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Đang Thực Hiện")

        ds_benh_nhan = ChuoiKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__lt=today_end).filter(trang_thai=da_thanh_toan)

        serializer = ChuoiKhamSerializerSimple(ds_benh_nhan, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False,
            'data': data,
        }
        return Response(response_data)

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):

        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(phong_chuc_nang, many=True, context={"request": request})
        phong_chuc_nang_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Phong Chuc Nang", "data": phong_chuc_nang_data})
class DanhSachDoanhThuDichVu(APIView):
    def get(self, request, format=None):
        danh_sach_dich_vu = HoaDonChuoiKham.objects.all()

        serializer = HoaDonChuoiKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
        data = serializer.data

        return Response(data)

class DanhSachDoanhThuThuoc(APIView):
    def get(self, request, format=None):
        danh_sach_thuoc = HoaDonThuoc.objects.all()

        serializer = HoaDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
        data = serializer.data

        return Response(data)
class DanhSachBenhNhan(APIView):
    def get(self, request, format=None):
        danh_sach_benh_nhan = User.objects.filter(chuc_nang = 1)
        
        serializer = UserSerializer(danh_sach_benh_nhan, many=True, context={'request': request})
        data = serializer.data
        
        return Response(data)

from datetime import datetime, timedelta

class ThongTinBenhNhanTheoMa(APIView):
    def get(self, request, format = None):
        ma_benh_nhan = self.request.query_params.get('ma_benh_nhan')
        thong_tin_theo_ma = User.objects.get(id = ma_benh_nhan)

        serializer = UserSerializer(thong_tin_theo_ma, context={'request': request})

        data = {
            'thong_tin_theo_ma': serializer.data
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")
        # serializer = UserSerializer()


class DanhSachLichHenTheoBenhNhan(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if range_end == '':
            lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_bat_dau__gte=start))
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)
            lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=end, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_end, thoi_gian_bat_dau__gte=start))
            
        serializer = LichHenKhamSerializer(lich_hen, many=True, context={'request': request})

        data = serializer.data
        return Response(data)


class SetChoThanhToan(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)

        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.save()

        data = {
            "message" : "Thay đổi trạng thái thành công!"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

class SetXacNhanKham(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)

        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Xác Nhận")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.save()

        data = {
            "message" : "Thay đổi trạng thái thành công"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

# class DanhSachKetQuaKhamChuyenKhoa(APIView):
#     def get(self, request, format=None):
#         id = self.request.query_params.get('id', None)

#         ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.get(id)
        
# class HoaDonTongTheoNguoiDung(APIView):
#     def get(self, request, format = None)
#         benh_nhan
class PhanKhoaKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).first()
        if chuoi_kham:
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            # serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            data = serializer.data
            response = {
                'benh_nhan': user_id,
                'data': data
            }
            return Response(response)
        else:
            response = {
                'benh_nhan': user_id,
                'data': []
            }
            Response(response)

        response = {
            'benh_nhan': user_id,
            'data': []
        }

        return Response(response)
 
class DanhSachChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        danh_sach_lich_hen = user.benh_nhan_hen_kham.all()
        serializer = LichHenKhamUserSerializer(danh_sach_lich_hen, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class ChuoiKhamGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        lich_hen = user.benh_nhan_hen_kham.all().order_by("-thoi_gian_tao")[0]
        chuoi_kham_gan_nhat = lich_hen.danh_sach_chuoi_kham.all()[0]
        serializer = ChuoiKhamSerializerSimple(chuoi_kham_gan_nhat, context={'request': request})

        response = {
            "benh_nhan": user_id,
            "data": serializer.data,
        }

        return Response(response)
 
class KetQuaChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        ket_qua_tong_quat = chuoi_kham.ket_qua_tong_quat.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={'request': request})
        response = {
            'chuoi_kham': chuoi_kham_id,
            'data': serializer.data
        }
        return Response(response)
 
class DanhSachDonThuocBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id = user_id)
        danh_sach_don_thuoc = user.don_thuoc.all()
        serializer = DanhSachDonThuocSerializer(danh_sach_don_thuoc, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class DanhSachThuocBenhNhan(APIView):
    def get(self, request, format=None):
        don_thuoc_id = self.request.query_params.get('don_thuoc_id')
        don_thuoc = DonThuoc.objects.get(id=don_thuoc_id)
        danh_sach_thuoc = don_thuoc.ke_don.all()
        serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
        response = {
            'don_thuoc': don_thuoc_id,
            'data': serializer.data
        }
        return Response(response)
        # return HttpResponse(json.dumps(response, cls=UUIDEncoder))
 
class DichVuKhamTheoPhongChucNang(APIView):
    def get(request, self, format=None):
        phong_chuc_nang = PhongChucNangSerializerSimple()
        dich_vu_kham = DichVuKham.objects.all()

class DanhSachBenhNhanTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong = self.request.query_params.get('id')
        phong = PhongChucNang.objects.get(id=id_phong)
        danh_sach_dich_vu = phong.dich_vu_kham_theo_phong.all()

        danh_sach_phan_khoa = set()
        for dich_vu in danh_sach_dich_vu:
            for phan_khoa in dich_vu.phan_khoa_dich_vu.all():
                if phan_khoa:
                    danh_sach_phan_khoa.add(phan_khoa)
        
        serializer = PhanKhoaKhamSerializer(danh_sach_phan_khoa, many=True, context={'request': request})

        response = {
            'data': serializer.data,
        }
        return Response(response)
                
class DanhSachDichVuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong_chuc_nang = self.request.query_params.get('id_phong_chuc_nang', None)
        if id_phong_chuc_nang:
            dich_vu_kham = DichVuKham.objects.select_related('phong_chuc_nang').filter(phong_chuc_nang = id_phong_chuc_nang)
            serializer = DichVuKhamSerializer(dich_vu_kham, many=True, context={"request":request})
            response = {
                "error" : False,
                "status": status.HTTP_200_OK,
                "data"  : serializer.data
            }
            return Response(response)
        
class LichHenKhamSapToi(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.now()
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
        try:
            lich_hen_kham = LichHenKham.objects.filter(benh_nhan=user).filter(trang_thai=trang_thai).annotate(timediff=F('thoi_gian_bat_dau')).order_by('timediff')[0]
            
            if lich_hen_kham:
                # print(lich_hen_kham.thoi_gian_bat_dau)
                # if lich_hen_kham.thoi_gian_bat_dau <= now:
                #    return Response({'data': []})
                serializer = LichHenKhamSerializer(lich_hen_kham, context={'request': request})
                response = {
                    'data': serializer.data
                }
                return Response(response)
            else:
                response = {
                    'data': []
                }
                return Response(response)
        except :
            return Response({'data': []})
        
class DonThuocGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        user = User.objects.get(id=user_id)
        try:
            don_thuoc = DonThuoc.objects.filter(benh_nhan=user).order_by('-thoi_gian_tao')[0]
            if don_thuoc:
                serializer = DonThuocSerializer(don_thuoc, context={'request': request})
                response = {
                    'data': serializer.data
                }
                return Response(response)
            else:
                response = {
                    'data': []
                }
                return Response(response)
        except :
            return Response({'data': []})
        

class TatCaLichHenBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.localtime(timezone.now())
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai='Xác Nhận')[0]

        lich_hen = LichHenKham.objects.filter(benh_nhan=user, trang_thai=trang_thai).annotate(relevance=models.Case(
            models.When(thoi_gian_bat_dau__gte=now, then=1),
            models.When(thoi_gian_bat_dau__lt=now, then=2),
            output_field=models.IntegerField(),
        )).annotate(
        timediff=models.Case(
            models.When(thoi_gian_bat_dau__gte=now, then= F('thoi_gian_bat_dau') - now),
            models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
            # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
            output_field=models.DurationField(),
        )).order_by('relevance', 'timediff')

        upcoming_events = []
        past_events = []
        for lich in lich_hen:
            if lich.relevance == 1:
                upcoming_events.append(lich)
            elif lich.relevance == 2:
                past_events.append(lich)

        serializer_1 = LichHenKhamSerializer(upcoming_events, many=True, context={'request': request})
        serializer_2 = LichHenKhamSerializer(past_events, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'upcoming': serializer_1.data,
            'past': serializer_2.data,
        }

        return Response(response)

class DangKiLichHen(APIView):
    def post(self, request, format=None):
        serializer = BookLichHenKhamSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['benh_nhan']
            thoi_gian_bat_dau = serializer.validated_data['thoi_gian_bat_dau']
            
            user = User.objects.get(id=user_id)
            date_time_str = datetime.strptime(thoi_gian_bat_dau, '%Y-%m-%d %H:%M:%S')
            trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai='Đã Đặt Trước')[0]
            lich_hen = LichHenKham.objects.create(benh_nhan=user, thoi_gian_bat_dau=date_time_str, trang_thai = trang_thai)
            serializer_1 = LichHenKhamSerializerSimple(lich_hen, context={'request': request})
            serializer_2 = UserSerializer(user, context={'request': request})
            response = {
                'benh_nhan': serializer_2.data,
                'lich_hen': serializer_1.data,
            }
        # response = {
        #     'message': "oke"
        # }
        return Response(response)

class UserInfor(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, context={'request': request})
        response = {
            'user': serializer.data
        }
        return Response(response)