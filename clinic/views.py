import re
from typing import Match
from django.contrib.messages.api import error
from django.http import response
from finance.models import HoaDonChuoiKham, HoaDonLamSang, HoaDonThuoc, HoaDonTong
from rest_framework import serializers
from rest_framework import request
from rest_framework.fields import ChoiceField
from clinic.forms import ThuocForm, UserForm, CongTyForm, DichVuKhamForm, KetQuaTongQuatForm, LichHenKhamForm, PhongChucNangForm
from medicine.models import DonThuoc, KeDonThuoc, NhomThau, Thuoc, TrangThaiDonThuoc, CongTy
from medicine.models import DonThuoc, KeDonThuoc, Thuoc, ThuocLog, TrangThaiDonThuoc
from django.http.response import  JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
from django.db.models.functions import TruncDay
from django.db.models import Count, F, Sum, Q
from django.db import models
from clinic.models import ChuoiKham, DichVuKham, FileKetQua, FileKetQuaChuyenKhoa, FileKetQuaTongQuat, KetQuaChuyenKhoa, KetQuaTongQuat, LichHenKham, LichSuChuoiKham, LichSuTrangThaiKhoaKham, PhanKhoaKham, PhongChucNang, TrangThaiChuoiKham, TrangThaiKhoaKham, TrangThaiLichHen, User
from django.shortcuts import redirect, render
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, views
from django.shortcuts import resolve_url
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as auth_login

from rest_framework.views import APIView
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import decimal
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import authenticate, views as auth_views


from datetime import datetime
format = '%m/%d/%Y %H:%M %p'

format_2 = '%d/%m/%Y %H:%M'

def getSubName(name):
    lstChar = []
    lstString = name.split(' ')
    for i in lstString:
        lstChar.append(i[0].upper())
    subName = "".join(lstChar)
    return subName


@login_required(login_url='/dang_nhap/')
def index(request):
    nguoi_dung = User.objects.filter(chuc_nang=1)
    # * tổng số bệnh nhân
    ds_bac_si = User.objects.filter(chuc_nang='3')
    # tong_so_benh_nhan = benh_nhan.count()

    # * tổng số hóa đơn
    # tong_so_hoa_don = ChuoiKham.objects.select_related('benh_nhan').all().count()

    # * tổng số đơn thuốc
    # tong_so_don_thuoc = DonThuoc.objects.select_related('benh_nhan').all().count()

    # * Danh sách dịch vụ khám
    danh_sach_dich_vu = DichVuKham.objects.all()

    # * danh sách bệnh nhân chưa được khám
    trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
    da_dat_truoc = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Đã đặt trước")[0]
    danh_sach_benh_nhan = LichHenKham.objects.select_related("benh_nhan").filter(trang_thai = trang_thai)
    danh_sach_lich_hen_chua_xac_nhan = LichHenKham.objects.select_related("benh_nhan").filter(trang_thai=da_dat_truoc)

    now = timezone.localtime(timezone.now())
    tomorrow = now + timedelta(1)
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end = tomorrow.replace(hour=0, minute=0, second=0)
    lich_hen = LichHenKham.objects.filter(trang_thai = trang_thai).annotate(relevance=models.Case(
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
    # today_events = LichHenKham.objects.filter(trang_thai = trang_thai, thoi_gian_bat_dau__lte=today_end)
    for lich in lich_hen:
        if lich.relevance == 1:
            upcoming_events.append(lich)
        elif lich.relevance == 2:
            past_events.append(lich)


    starting_day = datetime.now() - timedelta(days=7)

    user_data = User.objects.filter(thoi_gian_tao__gt=starting_day).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id"))
    users = [x["c"] for x in user_data]
    new_users = sum(users)
    labels = [x["day"].strftime("%Y-%m-%d") for x in user_data]

    user_trong_ngay = User.objects.filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end)

    hoa_don_chuoi_kham = HoaDonChuoiKham.objects.filter(thoi_gian_tao__gt=starting_day).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
    tong_tien = [str(x['total_spent']) for x in hoa_don_chuoi_kham]
    days = [x["day"].strftime("%Y-%m-%d") for x in hoa_don_chuoi_kham ]
    
    data = {
        'user': request.user,
        # 'tong_so_benh_nhan': tong_so_benh_nhan,
        # 'tong_so_hoa_don': tong_so_hoa_don,
        # 'tong_so_don_thuoc': tong_so_don_thuoc,
        'danh_sach_benh_nhan': danh_sach_benh_nhan,
        'lich_hen_chua_xac_nhan': danh_sach_lich_hen_chua_xac_nhan,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        # 'today_events': today_events,
        'users': users,
        "new_users_count": new_users, 
        'labels': labels,
        'ds_bac_si': ds_bac_si,
        'danh_sach_dich_vu': danh_sach_dich_vu,
        'nguoi_dung': nguoi_dung,
        'user_trong_ngay': user_trong_ngay,
        'tong_tien_chuoi_kham': tong_tien, 
        'thoi_gian_chuoi_kham': days,

    }
    return render(request, 'index.html', context=data)

def danh_sach_benh_nhan(request):
    danh_sach_benh_nhan = User.objects.filter(chuc_nang = 1)
    trang_thai = TrangThaiLichHen.objects.all()
    
    data = {
        'danh_sach_benh_nhan': danh_sach_benh_nhan,
        'trang_thai': trang_thai,
    }
    return render(request, 'le_tan/danh_sach_benh_nhan.html', context=data)

def update_benh_nhan(request, **kwargs):
    id_benh_nhan = kwargs.get('id')
    instance = get_object_or_404(User, id=id_benh_nhan)
    form = UserForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_benh_nhan': id_benh_nhan,
    }
    return render(request, 'le_tan/update_benh_nhan.html', context=data)

def cap_nhat_thong_tin_benh_nhan(request):
    if request.method == "POST":
        id_benh_nhan  = request.POST.get('id_benh_nhan')
        ho_ten        = request.POST.get('ho_ten')
        email         = request.POST.get('email')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        cmnd_cccd     = request.POST.get('cmnd_cccd')
        dia_chi       = request.POST.get('dia_chi')
        benh_nhan = get_object_or_404(User, id=id_benh_nhan)
        benh_nhan.ho_ten        = ho_ten
        benh_nhan.so_dien_thoai = so_dien_thoai
        benh_nhan.email         = email
        benh_nhan.cmnd_cccd     = cmnd_cccd
        benh_nhan.dia_chi       = dia_chi
        benh_nhan.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        # return redirect('/danh_sach_benh_nhan/')
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'


    def get_success_url(self):
        return resolve_url('index')

# * Chức năng Lễ Tân
# TODO đăng kí tài khoản cho bệnh nhân tại giao diện dashboard
# TODO xem lịch hẹn khám của bệnh nhân, sau đó xác nhận lại vs bác sĩ và cập nhật lại thời gian cho lịch hẹn khám

def lich_hen_kham_list(request):
    """ Trả về danh sách lịch hẹn của người dùng mới đặt lịch khám """
    trang_thai = TrangThaiLichHen.objects.get(ten_trang_thai="Đã đặt trước")
    lich_kham = LichHenKham.objects.filter(trang_thai=trang_thai).order_by("-thoi_gian_tao")
    data = {
        'lich_kham': lich_kham
    }
    return render(request, 'index.html', context=data)

def cap_nhat_lich_kham(request, *args, **kwargs):
    # NOTE function này chỉ là dùng khi lễ tân bấm xác nhận, sẽ thay đổi trạng thái của lịch hẹn,
    # NOTE chưa bao gồm thay đổi thời gian của lịch hẹn 
    pk = kwargs.get('pk')
    trang_thai_xac_nhan = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
    lich_hen = get_object_or_404(LichHenKham, pk=pk)
    lich_hen.trang_thai = trang_thai_xac_nhan
    lich_hen.nguoi_phu_trach = request.user
    lich_hen.save()
    return JsonResponse({
        'message': 'Cap Nhat Thanh Cong'
    })

class CapNhatLichKhamAPIToggle(APIView):
    # NOTE: sử dụng toggle này khi kết hợp với ajax, với mục đích là xác nhận lịch hẹn khám
    def get(self, request, format=None, *kwargs):
        pk = kwargs.get('pk')
        obj = get_object_or_404(LichHenKham, pk=pk)
        user_ = self.request.user
        trang_thai_xac_nhan = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
        obj.trang_thai = trang_thai_xac_nhan
        obj.nguoi_phu_trach = user_
        obj.save()
        data = {"message": "Cap Nhat Thanh Cong"}
        return Response(data)
        
# tạo người dùng
def create_user(request):
    if request.method == "POST":
        ho_ten        = request.POST.get("ho_ten", None)
        so_dien_thoai = request.POST.get("so_dien_thoai", None)
        password      = request.POST.get("password", None)
        cmnd_cccd     = request.POST.get("cmnd_cccd", None)
        dia_chi       = request.POST.get("dia_chi", None)

        if len(ho_ten) == 0:
            return HttpResponse(json.dumps({'message': "Họ Tên Không Được Trống", 'status': '400'}), content_type='application/json; charset=utf-8')

        if User.objects.filter(so_dien_thoai=so_dien_thoai).exists():
            return HttpResponse(json.dumps({'message': "Số Điện Thoại Đã Tồn Tại", 'status': '409'}), content_type='application/json; charset=utf-8')

        if User.objects.filter(cmnd_cccd=cmnd_cccd).exists():
            return HttpResponse(json.dumps({'message': "Số chứng minh thư đã tồn tại", 'status': '403'}), content_type = 'application/json; charset=utf-8')

        user = User.objects.create_user(
            ho_ten = ho_ten, 
            so_dien_thoai = so_dien_thoai, 
            password=password,
            cmnd_cccd = cmnd_cccd,
            dia_chi = dia_chi
        )
        user.save()

        response = {
            "message": "Đăng Kí Người Dùng Thành Công",
            "ho_ten": user.ho_ten,
            "so_dien_thoai": user.so_dien_thoai,
        }

        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def create_dich_vu(request):
    if request.method == "POST":
        bac_si_phu_trach = request.POST.get("bac_si_phu_trach", None)
        ten_dich_vu = request.POST.get("ten_dich_vu")

        if not bac_si_phu_trach:
            return HttpResponse(json.dumps({'message': "Vui Lòng Chọn Đúng Bác Sĩ", 'status': '400'}), content_type='application/json; charset=utf-8')
        else:
            bac_si = User.objects.get(id=bac_si_phu_trach)
        
        if len(ten_dich_vu) == 0:
            return HttpResponse(json.dumps({'message': "Tên Dịch Vụ Không Được Bỏ Trống", 'status': '400'}), content_type='application/json; charset=utf-8')

        if DichVuKham.objects.filter(ten_dich_vu = ten_dich_vu).exists():
            return HttpResponse(json.dumps({'message': "Dịch Vụ Đã Tồn Tại", 'status': '409'}), content_type='application/json; charset=utf-8')

        dich_vu_kham = DichVuKham.objects.create(ten_dich_vu=ten_dich_vu, bac_si_phu_trach=bac_si)
        dich_vu_kham.save()

        response = {
            "message": "Tạo Dịch Vụ Thành Công",
        }

        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(
            json.dumps({"message": "this isn't happening"}),
            content_type="application/json"
        )

# def create_lich_hen_kham(request):
    # if request.method == "POST":
    #     id_benh_nhan      = request.POST.get("id_benh_nhan", None)
    #     thoi_gian_bat_dau = request.POST.get("thoi_gian_bat_dau")
    #     user              = User.objects.get(id = id_benh_nhan)
        
    #     print(id_benh_nhan)
        # if len(thoi_gian_bat_dau) == 0:
        #     return HttpResponse(json.dumps({'message': "Thời gian không được bỏ trống", 'status': '400'}), content_type='application/json; charset=utf-8')

        # lich_hen_kham = LichHenKham.objects.create(benh_nhan=user, thoi_gian_bat_dau=thoi_gian_bat_dau)
        # lich_hen_kham.save()

        # response = {
        #     "message": "Thêm Lịch Hẹn Thành Công",
        # }

    # return HttpResponse(json.dumps("clicked"), content_type='application/json; charset=utf-8')

def add_lich_hen(request):      
    if request.method == "POST":
        id_benh_nhan = request.POST.get('id_benh_nhan')[0]
        thoi_gian_bat_dau = request.POST.get('thoi_gian_bat_dau')
        user = User.objects.get(id=id_benh_nhan)

        thoi_gian_bat_dau = datetime.strptime(thoi_gian_bat_dau, format_2)
        thoi_gian = thoi_gian_bat_dau.strftime("%Y-%m-%d %H:%M")

        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Xác Nhận")[0]
        lich_hen = LichHenKham.objects.create(
            benh_nhan         = user, 
            nguoi_phu_trach   = request.user, 
            thoi_gian_bat_dau = thoi_gian, 
            trang_thai        = trang_thai,
        )
        lich_hen.save()

        # response = {
        #     'message': id_benh_nhan
        # }
        response = {
            'message' : "Thêm Lịch Hẹn Thành Công!",
            'benh_nhan': user.ho_ten,
        }
        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

# def create_thuoc(request):
#     if request.method == "POST":
#         ten_thuoc         = request.POST.get("ten_thuoc")
#         ma_thuoc          = request.POST.get("ma_thuoc")
#         gia_mua           = request.POST.get("gia_nhap")
#         gia_ban           = request.POST.get("gia_ban")
#         mo_ta             = request.POST.get("mo_ta")
#         tac_dung_phu      = request.POST.get("tac_dung_phu")
#         quy_cach          = request.POST.get("quy_cach_dong_goi")
#         so_luong_kha_dung = request.POST.get("so_luong_nhap_lan_dau")

#         thuoc = Thuoc.objects.create(
#             ten_thuoc         = ten_thuoc, 
#             ma_thuoc          = ma_thuoc, 
#             gia_mua           = gia_mua, 
#             gia_ban           = gia_ban, 
#             mo_ta             = mo_ta,
#             tac_dung_phu      = tac_dung_phu,
#             quy_cach          = quy_cach,
#             so_luong_kha_dung = so_luong_kha_dung
#         )

#         response = {
#             "message": "Them thuốc mới thành công"
#         }

#         return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def create_thuoc(request):
    if request.method == "POST":
        ten_thuoc         = request.POST.get("ten_thuoc")
        ma_thuoc          = request.POST.get("ma_thuoc")
        gia_mua           = request.POST.get("gia_nhap")
        gia_ban           = request.POST.get("gia_ban")
        mo_ta             = request.POST.get("mo_ta")
        tac_dung_phu      = request.POST.get("tac_dung_phu")
        quy_cach          = request.POST.get("quy_cach_dong_goi")
        so_luong_kha_dung = request.POST.get("so_luong_nhap_lan_dau")
        id_cong_ty        = request.POST.get('id_cong_ty')

        cong_ty = CongTy.objects.get(id=id_cong_ty)

        thuoc = Thuoc.objects.create(
            ten_thuoc         = ten_thuoc, 
            ma_thuoc          = ma_thuoc, 
            gia_mua           = gia_mua, 
            gia_ban           = gia_ban, 
            mo_ta             = mo_ta, 
            tac_dung_phu      = tac_dung_phu, 
            quy_cach          = quy_cach, 
            so_luong_kha_dung = so_luong_kha_dung, 
            id_cong_ty        = cong_ty
        )
        return HttpResponse({'clicked'})

# * function này không cần dùng tới template
def create_dich_vu_kham(request):
    if request.is_ajax and request.method == "POST":
        form = DichVuKhamForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [ instance, ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    # some error occured
    return JsonResponse({"error": ""}, status=400)

def create_lich_hen_kham(request):
    if request.is_ajax and request.method == "POST":
        form = LichHenKhamForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [ instance, ])
            # send to client side.

            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    # some error occured
    return JsonResponse({"error": ""}, status=400)


class BatDauChuoiKhamAPIToggle(APIView):
    """ 
    * Khi bác sĩ lâm sàng bấm bắt đầu khám cho một bệnh nhân nào đó, thì chuỗi khám sẽ tự động được tạo
    """
    def get(self, request, format=None, **kwargs):
        user_id = kwargs.get('id')
        user = get_object_or_404(User, id=user_id)
        bac_si_lam_sang = self.request.user
        now = timezone.localtime(timezone.now())
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang thực hiện")[0]
        chuoi_kham = ChuoiKham.objects.create(
            benh_nhan = user,
            bac_si_dam_nhan = bac_si_lam_sang,
            thoi_gian_bat_dau = now,
            trang_thai = trang_thai
        )
        chuoi_kham.save()
        messages.success(request, 'Bắt đầu chuỗi khám')
        data = {
            "message": "Chuỗi Khám Bắt Đầu"
        }
        return Response(data)

class KetThucChuoiKhamAPI(APIView):
    """ 
    * Khi bác sĩ lâm sàng bấm kết thúc chuỗi khám thì chuỗi khám của người dùng sẽ được cập nhật thêm thời gian kết thúc và sẽ chuyển trạng thái sang Hoàn thành
    """

    def get(self, request, format=None, **kwargs):
        chuoi_kham_id = kwargs.get('id', None)
        if chuoi_kham_id == None:
            messages.error(request, 'Không thể kết thúc chuỗi khám')
            messages.debug(request, f'Chuỗi khám không tồn tại (id:{chuoi_kham_id})')
            return Response({
                "message": "Khong The Ket Thuc Chuoi Kham Vi Chua Bat Dau Chuoi Kham"
            })
        else:
            trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Hoàn Thành")[0]
            chuoi_kham = get_object_or_404(ChuoiKham, pk = chuoi_kham_id)
            chuoi_kham.thoi_gian_ket_thuc = timezone.localtime(timezone.now())
            chuoi_kham.trang_thai = trang_thai
            chuoi_kham.save()
            messages.success(request, 'Kết thúc chuỗi khám')
        data = {
            "message": "Ket Thuc Chuoi Kham"
        }
        return Response(data)

    # * Đoạn này dùng để sắp xếp lịch hẹn theo trình từ upcoming-past
    # * upcoming events: ascendant order
    # * past events: descendant order
    #     LichHenKham.objects.annotate(relevance=models.Case(
    #     models.When(thoi_gian_bat_dau__gte=now, then=1),
    #     models.When(thoi_gian_bat_dau__lt=now, then=2),
    #     output_field=models.IntegerField(),
    # )).annotate(
    # timediff=models.Case(
    #     models.When(thoi_gian_bat_dau__gte=now, then=F('thoi_gian_bat_dau') - now),
    #     models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
    #     output_field=models.DurationField(),
    # )).order_by('relevance', 'timediff')

# TODO hiển thị danh sách bệnh nhân chờ khám đối với từng phòng chức năng

def danh_sach_bn_theo_pcn(request, *args, **kwargs):

    """ 
    * method này sẽ trả về danh sách các bệnh nhân đã được phân khoa khám, cần khám
    * đối với từng phòng chức năng
    
    example:
                                  DichVuKham1 --> Phong Chuc Nang 1
                                |
    - user1 --> Chuoi Kham A -->  DichVuKham2 --> Phong Chuc Nang 2 
                                |
                                  DichVuKham3 --> Phong Chuc Nang 3

                                  DichVuKham1 --> Phong Chuc Nang 1
                                |
    - user2 --> Chuoi Kham B --> 
                                |
                                  DichVuKham3 --> Phong Chuc Nang 3

    ==> Phong Chuc Nang 1: [user1, user2]
    ==> Phong Chuc Nang 2: [user1,]
    ==> Phong Chuc Nang 3: [user1, user2]

    """
    id_phong = request.POST.get('id', None)
    phong_chuc_nang = get_object_or_404(PhongChucNang, id=id_phong)
    dich_vu_kham = phong_chuc_nang.dich_vu_kham

    # NOTE phần này sẽ thêm filter để lọc ra những bệnh nhân nào chưa khám 
    list_dich_vu = dich_vu_kham.dich_vu_kham.all()
    data = {
        "danh_sach_benh_nhan": list_dich_vu,
        "phong_chuc_nang": phong_chuc_nang,
        "dich_vu_kham": dich_vu_kham
    }
    return render(request, 'temlate.html', context=data)

def danh_sach_benh_nhan_cho(request):
    trang_thai = TrangThaiLichHen.objects.all()
    trang_thai_ck = TrangThaiChuoiKham.objects.all()
    return render(request, 'bac_si_lam_sang/danh_sach_benh_nhan_cho.html', context={"trang_thai": trang_thai, "trang_thai_ck": trang_thai_ck})

def phong_chuyen_khoa(request):
    # phong_chuc_nang = PhongChucNang.objects.values('ten_phong_chuc_nang').distinct()
    phong_chuc_nang = PhongChucNang.objects.all()

    trang_thai = TrangThaiChuoiKham.objects.all()
    data = {
        'phong_chuc_nang': phong_chuc_nang,
        'trang_thai': trang_thai,
    }
    return render(request, 'bac_si_chuyen_khoa/phong_chuyen_khoa.html', context=data)

def phan_khoa_kham(request, **kwargs):
    id_lich_hen = kwargs.get('id_lich_hen', None)
    lich_hen    = LichHenKham.objects.get(id = id_lich_hen)
    data = {
        'id_lich_hen': id_lich_hen,
        'lich_hen'   : lich_hen,
    }
    return render(request, 'bac_si_lam_sang/phan_khoa_kham.html', context=data)

def store_phan_khoa(request):
    if request.method == "POST":
        request_data = request.POST.get('data', None)
        user         = request.POST.get('user', None)
        id_lich_hen  = request.POST.get('id_lich_hen', None)
        data         = json.loads(request_data)

        now       = datetime.now()
        date_time = now.strftime("%m%d%y%H%M%S")

        bulk_create_data = []
        user = User.objects.get(id = user)
        subName = getSubName(user.ho_ten)
        ma_hoa_don = "HD" + "-" + subName + '-' + date_time

        lich_hen = LichHenKham.objects.get(id = id_lich_hen)
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Phân Khoa")[0]
        lich_hen.trang_thai = trang_thai_lich_hen
        lich_hen.save()
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Chờ Thanh Toán")[0]
        chuoi_kham = ChuoiKham.objects.get_or_create(bac_si_dam_nhan=request.user, benh_nhan=user, trang_thai=trang_thai, lich_hen = lich_hen)[0]
        chuoi_kham.save()
        hoa_don = HoaDonChuoiKham.objects.create(chuoi_kham=chuoi_kham, ma_hoa_don=ma_hoa_don)
        hoa_don.save()


        for i in data:
            index = data.index(i)
            priority = index + 1
            dich_vu = DichVuKham.objects.only('id').get(id=i['obj']['id'])
            bac_si = request.user
            bulk_create_data.append(PhanKhoaKham(benh_nhan=user, dich_vu_kham=dich_vu, bao_hiem=i['obj']['bao_hiem'], bac_si_lam_sang=bac_si, chuoi_kham=chuoi_kham, priority=priority))

        PhanKhoaKham.objects.bulk_create(bulk_create_data)

        response = {
            'status' : 200,
            'message': "Phân Khoa Khám Thành Công!",
            'url' : '/bac_si_lam_sang/danh_sach_benh_nhan_cho/'
        }

        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def store_ke_don(request):
    if request.method == "POST":
        request_data = request.POST.get('data', None)
        user = request.POST.get('user', None)
        data = json.loads(request_data)

        now = datetime.now()
        date_time = now.strftime("%m%d%y%H%M%S")

        bulk_create_data = []
        user = User.objects.get(id=user)
        subName = getSubName(user.ho_ten)
        ma_don_thuoc = subName + '-' + date_time
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Chờ Thanh Toán")[0]
        don_thuoc = DonThuoc.objects.get_or_create(benh_nhan=user, bac_si_ke_don=request.user, trang_thai=trang_thai, ma_don_thuoc=ma_don_thuoc)[0]
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Hóa Đơn Thuốc")[0]
        # lich_hen = 
        don_thuoc.save()

        for i in data:
            thuoc = Thuoc.objects.only('id').get(id=i['obj']['id'])
            ke_don_thuoc = KeDonThuoc(don_thuoc=don_thuoc, thuoc=thuoc, so_luong=i['obj']['so_luong'], cach_dung=i['obj']['duong_dung'], ghi_chu=i['obj']['ghi_chu'], bao_hiem=i['obj']['bao_hiem'])
            bulk_create_data.append(ke_don_thuoc)

        KeDonThuoc.objects.bulk_create(bulk_create_data)
        response = {'status': 200, 'message': 'Kê Đơn Thành Công', 'url': '/danh_sach_kham/'}
        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def files_upload_view(request):
    print(request.FILES)
    if request.method == "POST":
        ma_ket_qua = request.POST.get('ma_ket_qua', None)
        mo_ta = request.POST.get('mo_ta', None)
        ket_luan = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        print(id_chuoi_kham)

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        # chuoi_kham = ChuoiKham.objects.get(id=16)
        # ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)[0]
        
        # for value in request.FILES.values():
        #     file = FileKetQua.objects.create(file=value)
        #     file_kq_tong_quat = FileKetQuaTongQuat.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, file=file)
        #     file_kq_tong_quat.save()

        return HttpResponse('upload')
    return JsonResponse({'post': False})

def upload_files_chuyen_khoa(request):

    if request.method == "POST":
        ma_ket_qua    = request.POST.get('ma_ket_qua', None)
        mo_ta         = request.POST.get('mo_ta', None)
        ket_luan      = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)

        for value in request.FILES.values():
            file = FileKetQua.objects.create(file=value)
            file_kq_chuyen_khoa = FileKetQuaChuyenKhoa.objects.create(ket_qua_chuyen_khoa=ket_qua_chuyen_khoa, file=file)
        
        return HttpResponse('upload')
    response = {
        'status': 200,
        'message' : 'Upload Thành Công!'
    }
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def upload_files_lam_sang(request):
    print(request.FILES)
    if request.method == "POST":
        ma_ket_qua = request.POST.get('ma_ket_qua', None)
        mo_ta = request.POST.get('mo_ta', None)
        ket_luan = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_tong_quat.ma_ket_qua = ma_ket_qua
        ket_qua_tong_quat.mo_ta = mo_ta
        ket_qua_tong_quat.ket_luan = ket_luan
        ket_qua_tong_quat.save()

        for value in request.FILES.values():
            file = FileKetQua.objects.create(file=value)
            file_ket_qua_tong_quat = FileKetQuaTongQuat.objects.create(file=file, ket_qua_tong_quat=ket_qua_tong_quat)

        return HttpResponse('upload')
    return JsonResponse({'post': False})

def upload_view(request, **kwargs):
    id_chuoi_kham = kwargs.get('id')
    data = {
        'id_chuoi_kham' : id_chuoi_kham,
    }
    return render(request, 'bac_si_chuyen_khoa/upload.html', context=data)

def upload_view_lam_sang(request, **kwargs):
    id_chuoi_kham = kwargs.get('id')
    data = {
        'id_chuoi_kham' : id_chuoi_kham,
    }
    return render(request, 'bac_si_lam_sang/upload_ket_qua.html', context=data)

def phong_tai_chinh_danh_sach_cho(request):
    trang_thai = TrangThaiChuoiKham.objects.all()
    data = {
        'trang_thai' : trang_thai,
    }
    return render(request, 'phong_tai_chinh/danh_sach_thanh_toan.html', context= data)

def phong_thuoc_danh_sach_cho(request):
    return render(request, 'phong_thuoc/danh_sach_cho.html')

def hoa_don_dich_vu(request, **kwargs):
    id_chuoi_kham = kwargs.get('id_chuoi_kham')
    # chuoi_kham = ChuoiKham.objects.filter(benh_nhan__id=user_id, trang_thai__id = 4)[0]
    chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
    hoa_don_dich_vu = chuoi_kham.hoa_don_dich_vu
    phan_khoa_kham = chuoi_kham.phan_khoa_kham.all()
    tong_tien = []
    for khoa_kham in phan_khoa_kham:
        if khoa_kham.bao_hiem:
            # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
            gia = khoa_kham.dich_vu_kham.don_gia
        else:
            gia = khoa_kham.dich_vu_kham.don_gia
        tong_tien.append(gia)
    total_spent = sum(tong_tien)
    tong_tien.clear()
    data = {
        'chuoi_kham'     : chuoi_kham,
        'hoa_don_dich_vu': hoa_don_dich_vu,
        'phan_khoa_kham' : phan_khoa_kham,
        'tong_tien'      : total_spent,
    }
    return render(request, 'phong_tai_chinh/hoa_don_dich_vu.html', context=data)


def hoa_don_thuoc(request, **kwargs):
    id_don_thuoc = kwargs.get('id_don_thuoc')
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()

    tong_tien = []
    for thuoc_instance in danh_sach_thuoc:
        gia = int(thuoc_instance.thuoc.don_gia_tt) * thuoc_instance.so_luong
        tong_tien.append(gia)
    
    total_spent = sum(tong_tien)
    tong_tien.clear()
    
    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'tong_tien' : total_spent,
        'don_thuoc' : don_thuoc,
    }

    return render(request, 'phong_tai_chinh/hoa_don_thuoc.html', context=data)

def don_thuoc(request, **kwargs):
    id_don_thuoc = kwargs.get('id_don_thuoc')
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()

    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'don_thuoc' : don_thuoc,
    }
    return render(request, 'phong_thuoc/don_thuoc.html', context=data)

def danh_sach_kham(request):
    trang_thai = TrangThaiLichHen.objects.all()
    trang_thai_ck = TrangThaiChuoiKham.objects.all()
    return render(request, 'bac_si_lam_sang/danh_sach_kham.html', context={"trang_thai": trang_thai, "trang_thai_ck": trang_thai_ck})

# def thanh_toan_hoa_don_dich_vu(request):
    

def login(request):
    return render(request, 'registration/login.html')

class BatDauChuoiKhamToggle(APIView):
    def get(self, request, format=None, **kwargs):
        id_phan_khoa = request.GET.get('id', None)
        print(id_phan_khoa)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        chuoi_kham = phan_khoa_kham.chuoi_kham
        now = timezone.localtime(timezone.now())
        if phan_khoa_kham.priority == 1:
            chuoi_kham.thoi_gian_bat_dau = now
            phan_khoa_kham.thoi_gian_bat_dau = now
            chuoi_kham.save()
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Bắt Đầu Chuỗi Khám, Dịch Vụ Khám Đầu Tiên: {dich_vu}', 'time': f'{now}'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        else:
            phan_khoa_kham.thoi_gian_bat_dau = now
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Bắt Đầu Dịch Vụ: {dich_vu}', 'time': f'{now}'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
 
class KetThucChuoiKhamToggle(APIView):
    def get(self, request, format=None, **kwargs):
        id_phan_khoa = request.GET.get('id', None)
        print(id_phan_khoa)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        chuoi_kham = phan_khoa_kham.chuoi_kham
        priotity = chuoi_kham.phan_khoa_kham.all().aggregate(Max('priority'))
        now = timezone.localtime(timezone.now())
        print(priotity['priority__max'])
        if phan_khoa_kham.priority == priotity['priority__max']:
            chuoi_kham.thoi_gian_ket_thuc = now
            phan_khoa_kham.thoi_gian_ket_thuc = now
            chuoi_kham.save()
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Kết Thúc Chuỗi Khám, Dịch Vụ Khám Cuối Cùng: {dich_vu}', 'time': f'{now}'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        else:
            phan_khoa_kham.thoi_gian_ket_thuc = now
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Kết Thúc Dịch Vụ: {dich_vu}', 'time': f'{now}'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def bat_dau_chuoi_kham(request, **kwargs):
    id_phan_khoa = kwargs.get('id', None)
    phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
    chuoi_kham = phan_khoa_kham.chuoi_kham
    now = timezone.localtime(timezone.now())
    if phan_khoa_kham.priority == 1:
        chuoi_kham.thoi_gian_bat_dau = now
        phan_khoa_kham.thoi_gian_bat_dau = now
        chuoi_kham.save()
        phan_khoa_kham.save()
        dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
        response = {'status': '200', 'message': f'Bắt Đầu Chuỗi Khám, Dịch Vụ Khám: {dich_vu}', 'time': f'{now}'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    else:
        phan_khoa_kham.thoi_gian_bat_dau = now
        phan_khoa_kham.save()
        dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
        response = {'status': '200', 'message': f'Bắt Đầu Dịch Vụ: {dich_vu}', 'time': f'{now}'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def danh_sach_thuoc(request):
    return render(request, 'phong_thuoc/danh_sach_thuoc.html')

def danh_sach_thuoc_phong_tai_chinh(request):
    nhom_thau = NhomThau.objects.all()
    data={
        'nhom_thau': nhom_thau
    }
    return render(request, 'phong_tai_chinh/danh_sach_thuoc.html', context = data)

def them_moi_thuoc_phong_tai_chinh(request):
    cong_ty = CongTy.objects.all()
    data = {
        'cong_ty': cong_ty
    }
    return render(request, 'phong_tai_chinh/them_moi_thuoc.html', context=data)

def cong_ty(request):
    return render(request, 'phong_tai_chinh/nguon_cung.html')

def update_lich_hen(request, **kwargs):
    id_lich_hen = kwargs.get('id')
    lich_hen_kham = LichHenKham.objects.get(id=id_lich_hen)
    data = {
        'lich_hen' : lich_hen_kham,
    }
    return render(request, 'le_tan/update_lich_hen.html', context=data)

def danh_sach_lich_hen(request):
    trang_thai = TrangThaiLichHen.objects.all()
    nguoi_dung = User.objects.filter(chuc_nang=1)
    data = {
        'trang_thai' : trang_thai,
        'nguoi_dung' : nguoi_dung,
    }
    return render(request, 'le_tan/danh_sach_lich_hen.html', context=data)


def store_update_lich_hen(request):
    if request.method == 'POST':
        thoi_gian_bat_dau = request.POST.get('thoi_gian_bat_dau')
        id_lich_hen = request.POST.get('id')
        thoi_gian_bat_dau = datetime.strptime(thoi_gian_bat_dau, format_2)
        thoi_gian = thoi_gian_bat_dau.strftime("%Y-%m-%d %H:%M")
        lich_hen = LichHenKham.objects.get(id=id_lich_hen)
        lich_hen.thoi_gian_bat_dau = thoi_gian
        lich_hen.save()
        response = {
            "message" : "Them Thanh Cong"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def them_thuoc_phong_tai_chinh(request):
    return render(request, 'phong_tai_chinh/them_moi_thuoc.html')

@transaction.atomic
def xuat(request, id=None, so_luong=None):
    try:
        thuoc = Thuoc.objects.filter(id=id)
        print(thuoc[0].kha_dung, end="\n\n\n")
        if thuoc[0].kha_dung:
            thuoc.update(so_luong_kha_dung=F('so_luong_kha_dung') - so_luong)
            ThuocLog.objects.create(thuoc=thuoc[0], ngay=timezone.now(), quy_trinh=ThuocLog.OUT, so_luong=so_luong)
        else:
            return Response({"error": True, "message": "So Luong Thuoc Kha Dung = 0, Khong The Xuat Thuoc"})  
        return Response({"error": False, "message": f"Xuat Thuoc Thanh Cong: {so_luong} {thuoc[0].ten_thuoc}"})
    except:
        
        return Response({"error": True, "message": "Loi Tao Log Thuoc"})

class ThanhToanHoaDonThuocToggle(APIView):

    def get(self, request, format=None):
        id_don_thuoc    = request.GET.get('id', None)
        don_thuoc       = DonThuoc.objects.get(id = id_don_thuoc)
        danh_sach_thuoc = don_thuoc.ke_don.all()
        tong_tien       = request.GET.get('tong_tien', None)
        print(tong_tien)
        now             = datetime.now()
        date_time       = now.strftime("%m%d%y%H%M%S")
        ma_hoa_don      = "HDT-" + date_time
        
        hoa_don_thuoc = HoaDonThuoc.objects.create(don_thuoc=don_thuoc, ma_hoa_don=ma_hoa_don, tong_tien=tong_tien)
        try:
            for instance in danh_sach_thuoc:    
                id_thuoc = instance.thuoc.id 
                so_luong = instance.so_luong
                thuoc = Thuoc.objects.get(id=id_thuoc)
                ten_thuoc = thuoc.ten_thuoc

                xuat(request, id=id_thuoc, so_luong=so_luong)
            trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đã Thanh Toán")[0]
            don_thuoc.trang_thai=trang_thai
            don_thuoc.save()
            
            response = {'status': 200, 'message': 'Thanh Toán Thành Công'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        except:
            response = {'status': 404, 'message': 'Xảy Ra Lỗi Trong Quá Trình Thanh Toán'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

class ThanhToanHoaDonDichVuToggle(APIView):
    def get(self, request, format=None):
        ma_hoa_don                = request.GET.get('ma_hoa_don', None)
        hoa_don_dich_vu           = HoaDonChuoiKham.objects.get(ma_hoa_don = ma_hoa_don)
        tong_tien                 = request.GET.get('tong_tien', None)
        hoa_don_dich_vu.tong_tien = tong_tien
        hoa_don_dich_vu.save()

        # Set trạng thái chuỗi khám
        trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Đã Thanh Toán")[0]
        chuoi_kham = hoa_don_dich_vu.chuoi_kham
        chuoi_kham.trang_thai = trang_thai_chuoi_kham
        chuoi_kham.save()
        
        # Set trạng thái lịch hẹn
        lich_hen = chuoi_kham.lich_hen
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Dịch Vụ")[0]
        lich_hen.trang_thai = trang_thai_lich_hen
        lich_hen.save()
        
        response = {
            'status' : 200 ,
            'message': "Thanh Toán Thành Công!"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def thanh_toan_hoa_don_thuoc(request):
    id_don_thuoc = request.GET.get('id', None)
    tong_tien = request.GET.get('tong_tien', None)
    print(tong_tien)
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()
    now = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")
    ma_hoa_don = "HDT-" + date_time
    print(ma_hoa_don)
    
    try:
        for instance in danh_sach_thuoc:    
            id_thuoc = instance.thuoc.id
            so_luong = instance.so_luong
            thuoc = Thuoc.objects.get(id=id_thuoc)
            ten_thuoc = thuoc.ten_thuoc
            if thuoc.kha_dung:
                thuoc.update(so_luong_kha_dung = F('so_luong_kha_dung') - so_luong)
                thuoc.save()
                ThuocLog.objects.create(thuoc=thuoc, ngay=timezone.now(), quy_trinh=ThuocLog.OUT, so_luong=so_luong)
            else:
                response = {'status': 404, 'message': f'Số Lượng Thuốc Không Khả Dụng, Vui Lòng Kiểm Tra Lại Thuốc: {ten_thuoc}'}
                return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
        hoa_don_thuoc = don_thuoc.hoa_don_thuoc
        hoa_don_thuoc.ma_hoa_don = ma_hoa_don
        hoa_don_thuoc.save()
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đã Thanh Toán")[0]
        don_thuoc.update(trang_thai=trang_thai)
        don_thuoc.save()
        
        response = {'status': 200, 'message': 'Thanh Toán Thành Công'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    except:
        response = {'status': 404, 'message': 'Xảy Ra Lỗi Trong Quá Trình Thanh Toán'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def loginUser(request):
    so_dien_thoai = request.POST.get('so_dien_thoai')
    password = request.POST.get('password')
    
    user = authenticate(so_dien_thoai=so_dien_thoai, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return HttpResponse(json.dumps({'message': 'Success', 'url': '/index'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message': 'inactive'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'message': 'invalid'}), content_type="application/json")

def dung_kham(request):
    if request.method == "POST":
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        ly_do = request.POST.get('ly_do')
        chuoi_kham = ChuoiKham.objects.get(id = id_chuoi_kham)
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Dừng khám")[0]
        lich_su = LichSuChuoiKham.objects.create(chuoi_kham = chuoi_kham, trang_thai = trang_thai, chi_tiet_trang_thai = ly_do)
        chuoi_kham.trang_thai = trang_thai
        chuoi_kham.save()
        return HttpResponse(json.dumps({
            'status' : 200,
            'message' : "Đã dừng khám",
            'url': '/danh_sach_benh_nhan_cho'
        }), content_type="application/json")

# TODO Sửa lại phần dừng khám của bác sĩ lâm sàng, vì còn liên quan đến phần lịch hẹn

def dung_kham_chuyen_khoa(request):
    if request.method == "POST":
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        id_phan_khoa = request.POST.get('id_phan_khoa')
        ly_do = request.POST.get('ly_do')
        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Dừng khám")[0]
        trang_thai_phan_khoa = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham = "Dừng khám")[0]
        chuoi_kham.trang_thai = trang_thai
        chuoi_kham.save()
        phan_khoa_kham.trang_thai = trang_thai_phan_khoa
        phan_khoa_kham.save()
        lich_su_phan_khoa = LichSuTrangThaiKhoaKham.objects.create(phan_khoa_kham=phan_khoa_kham, trang_thai_khoa_kham=trang_thai_phan_khoa, chi_tiet_trang_thai=ly_do)
        lich_su_chuoi_kham = LichSuChuoiKham.objects.create(chuoi_kham=chuoi_kham, trang_thai=trang_thai,chi_tiet_trang_thai=ly_do)
        return HttpResponse(json.dumps({
            'status' : 200,
            'message' : "Đã dừng khám",
            'url': '/phong_chuyen_khoa'
        }), content_type="application/json")

def xoa_lich_hen(request):
    if request.method == "POST":
        id_lich_hen = request.POST.get('id')
        lich_hen = LichHenKham.objects.get(id=id_lich_hen)
        lich_hen.delete()
        return HttpResponse(json.dumps({
            'status' : 200,
            'url': '/danh_sach_lich_hen'
        }), content_type="application/json")

def update_nguon_cung(request, **kwargs):
    id_cong_ty = kwargs.get('id')
    instance = get_object_or_404(CongTy, id=id_cong_ty)
    form = CongTyForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_cong_ty': id_cong_ty
    }
    return render(request, 'le_tan/update_nguon_cung.html', context=data)

def chinh_sua_nguon_cung(request):
    if request.method == "POST":
        id_cong_ty = request.POST.get('id_cong_ty')
        ten_cong_ty = request.POST.get('ten_cong_ty')
        dia_chi = request.POST.get('dia_chi')
        giay_phep_kinh_doanh = request.POST.get('giay_phep_kinh_doanh')
        so_lien_lac = request.POST.get('so_lien_lac')
        email = request.POST.get('email')
        mo_ta = request.POST.get('mo_ta')
        cong_ty = get_object_or_404(CongTy, id=id_cong_ty)
        cong_ty.ten_cong_ty = ten_cong_ty
        cong_ty.dia_chi = dia_chi
        cong_ty.giay_phep_kinh_doanh = giay_phep_kinh_doanh
        cong_ty.so_lien_lac = so_lien_lac
        cong_ty.email = email
        cong_ty.mo_ta = mo_ta
        cong_ty.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def danh_sach_dich_vu_kham(request):
    return render(request, 'phong_tai_chinh/dich_vu_kham.html')

def update_dich_vu_kham(request, **kwargs):
    id = kwargs.get('id')
    print(id)
    instance = get_object_or_404(DichVuKham, id=id)
    dich_vu_kham_form = DichVuKhamForm(request.POST or None, instance=instance)

    data = {
        'dich_vu_kham_form': dich_vu_kham_form,
        'id'               : id,
    }
    return render(request, 'phong_tai_chinh/update_dich_vu_kham.html', context=data)

def chinh_sua_phong_chuc_nang(request):
    if request.method == "POST":
        id  = request.POST.get('id')
        ten_phong_chuc_nang = request.POST.get('ten_phong_chuc_nang')
        
        phong_chuc_nang = get_object_or_404(PhongChucNang, id=id)
        phong_chuc_nang.ten_phong_chuc_nang = ten_phong_chuc_nang
        phong_chuc_nang.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def update_user(request, **kwargs):
    id_user = kwargs.get('id')
    instance = get_object_or_404(User, id=id_user)
    form = UserForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_user': id_user,
    }
    return render(request, 'update_user.html', context=data)

def cap_nhat_user(request):
    if request.method == "POST":
        id_user       = request.POST.get('id_user')
        ho_ten        = request.POST.get('ho_ten')
        email         = request.POST.get('email')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        cmnd_cccd     = request.POST.get('cmnd')
        user = get_object_or_404(User, id=id_user)
        user.ho_ten        = ho_ten
        user.so_dien_thoai = so_dien_thoai
        user.email         = email
        user.cmnd_cccd     = cmnd_cccd
        user.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def chinh_sua_thuoc(request, **kwargs):
    id_thuoc = kwargs.get('id_thuoc')
    instance = get_object_or_404(Thuoc, id=id_thuoc)
    form = ThuocForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_thuoc': id_thuoc,
    }
    return render(request, 'phong_tai_chinh/update_thuoc.html', context=data)

def update_thuoc(request):
    if request.method == "POST":
        id_thuoc          = request.POST.get('id_thuoc')
        ten_thuoc         = request.POST.get('ten_thuoc')
        gia_mua           = request.POST.get('gia_mua')
        gia_ban           = request.POST.get('gia_ban')
        mo_ta             = request.POST.get('mo_ta')
        tac_dung_phu      = request.POST.get('tac_dung_phu')
        quy_cach          = request.POST.get('quy_cach')
        so_luong_kha_dung = request.POST.get('so_luong_kha_dung')
        id_cong_ty        = request.POST.get('id_cong_ty')

        id_cong_ty = CongTy.objects.get(id = id_cong_ty)
        thuoc = get_object_or_404(Thuoc, id = id_thuoc)
        thuoc.ten_thuoc         = ten_thuoc
        thuoc.gia_mua           = gia_mua
        thuoc.gia_ban           = gia_ban
        thuoc.mo_ta             = mo_ta
        thuoc.tac_dung_phu      = tac_dung_phu
        thuoc.quy_cach          = quy_cach
        thuoc.so_luong_kha_dung = so_luong_kha_dung
        thuoc.id_cong_ty        = id_cong_ty
        # thuoc.cong_ty           = i
        thuoc.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def chinh_sua_thuoc_phong_thuoc(request, **kwargs):
    id_thuoc = kwargs.get('id_thuoc')
    instance = get_object_or_404(Thuoc, id=id_thuoc)
    form = ThuocForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_thuoc': id_thuoc,
    }
    return render(request, 'phong_thuoc/update_thuoc.html', context=data)

def update_thuoc_phong_thuoc(request):
    if request.method == "POST":
        id_thuoc     = request.POST.get('id_thuoc')
        ten_thuoc    = request.POST.get('ten_thuoc')
        mo_ta        = request.POST.get('mo_ta')
        tac_dung_phu = request.POST.get('tac_dung_phu')
        quy_cach     = request.POST.get('quy_cach')

        thuoc = get_object_or_404(Thuoc, id = id_thuoc)
        
        thuoc.ten_thuoc    = ten_thuoc
        thuoc.mo_ta        = mo_ta
        thuoc.tac_dung_phu = tac_dung_phu
        thuoc.quy_cach     = quy_cach
        thuoc.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

# def get_thong_tin_benh_nhan(request):
#     id = User.objects.get(id = ma_benh_nhan)
    
def doanh_thu_phong_kham(request):
    return render(request, 'phong_tai_chinh/doanh_thu_phong_kham.html')

def them_dich_vu_kham_excel(request):
    return render(request, 'phong_tai_chinh/them_dich_vu_kham_excel.html')

def them_dich_vu_kham(request):
    '''Đây là trường hợp "and"'''
    # bac_si = User.objects.filter(Q(chuc_nang = 4) | Q(chuc_nang = 3))
    bac_si = User.objects.filter(chuc_nang = 4)
    data = {
        'bac_si': bac_si
    }
    return render(request, 'phong_tai_chinh/them_dich_vu_kham.html', context=data)

from decimal import Decimal
def import_dich_vu_excel(request):
    if request.method == 'POST':
        data             = request.POST.get('data')
        list_objects     = json.loads(data)
        bulk_create_data = []
        for obj in list_objects:
            stt             = obj['STT']
            ma_gia_key      = "MA_GIA"
            ma_cosokcb_key  = "MA_COSOKCB"
            ma_dvkt         = obj['MA_DVKT']
            ten_dvkt        = obj['TEN_DVKT']
            don_gia         = obj['DON_GIA']
            gia             = Decimal(don_gia)
            bao_hiem        = True
            quyet_dinh      = obj['QUYET_DINH']
            cong_bo         = obj['CONG_BO']
            phong_chuc_nang = obj['PHONG_CHUC_NANG']

            group_phong_chuc_nang = PhongChucNang.objects.get_or_create(ten_phong_chuc_nang = phong_chuc_nang)[0]

            if ma_gia_key in obj.keys():
                ma_gia = obj[ma_gia_key]
            else:
                ma_gia = ""
            if ma_cosokcb_key in obj.keys():
                ma_cosokcb = obj[ma_cosokcb_key]
            else:
                ma_cosokcb = ""
            # print(ma_gia)
            model = DichVuKham(
                stt             = stt,
                ma_dvkt         = ma_dvkt,
                ten_dvkt        = ten_dvkt,
                ma_gia          = ma_gia,
                don_gia         = gia,
                bao_hiem        = bao_hiem,
                quyet_dinh      = quyet_dinh,
                cong_bo         = cong_bo,
                ma_cosokcb      = ma_cosokcb,
                phong_chuc_nang = group_phong_chuc_nang
            )
            bulk_create_data.append(model)
        
        DichVuKham.objects.bulk_update_or_create(bulk_create_data,[
            'stt',
            'ma_dvkt',
            'ten_dvkt',
            'ma_gia',
            'don_gia',
            'bao_hiem',
            'quyet_dinh',
            'cong_bo',
            'ma_cosokcb',
            'phong_chuc_nang' 
        ], match_field = 'stt')

        response = {
            'status': 200,
            'message': 'Import Thanh Cong',
            'url' : '/danh_sach_dich_vu_kham/'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def them_thuoc_excel(request):
    return render(request, 'phong_tai_chinh/them_thuoc_excel.html')

def import_thuoc_excel(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        list_objects = json.loads(data)
        bulk_create_data = []

        for obj in list_objects:
            ma_thuoc_key      = "MA_THUOC_BV"
            ma_hoat_chat_key  = "MA_HOAT_CHAT"
            ma_cskcb_key      = "MA_CSKCB"
            ten_hoat_chat     = obj['HOAT_CHAT']
            duong_dung_key    = "DUONG_DUNG"
            ham_luong_key     = "HAM_LUONG"
            ten_thuoc         = obj['TEN_THUOC']
            so_dang_ky        = obj['SO_DANG_KY']
            dong_goi          = obj['DONG_GOI']
            don_vi_tinh       = obj['DON_VI_TINH']
            don_gia           = Decimal(obj['DON_GIA'])
            don_gia_tt        = Decimal(obj['DON_GIA_TT'])
            so_luong_kha_dung = obj['SO_LUONG']
            hang_sx           = obj['HANG_SX']
            nuoc_sx_key       = "NUOC_SX"
            quyet_dinh        = obj['QUYET_DINH']
            cong_bo           = obj['CONG_BO']
            loai_thuoc        = obj['LOAI_THUOC']
            loai_thau         = obj['LOAI_THAU']
            nhom_thau         = obj['NHOM_THAU']
            nha_thau          = obj['NHA_THAU']
            bao_hiem          = True

            group_nhom_thau = NhomThau.objects.get_or_create(ten_nhom_thau=nhom_thau)[0]
            group_cong_ty = CongTy.objects.get_or_create(ten_cong_ty=nha_thau)[0]
            

            if ma_hoat_chat_key in obj.keys():
                ma_hoat_chat = obj[ma_hoat_chat_key]
            else:
                ma_hoat_chat = ""

            if ma_cskcb_key in obj.keys():
                ma_cskcb = obj[ma_cskcb_key]
            else:
                ma_cskcb = ""

            if nuoc_sx_key in obj.keys():
                nuoc_sx = obj[nuoc_sx_key]
            else: 
                nuoc_sx = ""

            if ma_thuoc_key in obj.keys():
                ma_thuoc = obj[ma_thuoc_key]
            else:
                ma_thuoc = ""

            if duong_dung_key in obj.keys():
                duong_dung = obj[duong_dung_key]
            else:
                duong_dung = ""

            if ham_luong_key in obj.keys():
                ham_luong = obj[ham_luong_key]
            else:
                ham_luong = ""

            model = Thuoc(
                ma_thuoc          = ma_thuoc,
                ma_hoat_chat      = ma_hoat_chat, 
                ten_hoat_chat     = ten_hoat_chat, 
                duong_dung        = duong_dung,
                ham_luong         = ham_luong,
                ten_thuoc         = ten_thuoc,
                so_dang_ky        = so_dang_ky, 
                dong_goi          = dong_goi,
                don_vi_tinh       = don_vi_tinh,
                don_gia           = don_gia,
                don_gia_tt        = don_gia_tt,
                so_lo             = "",
                so_luong_kha_dung = so_luong_kha_dung,
                ma_cskcb          = ma_cskcb, 
                hang_sx           = hang_sx,
                nuoc_sx           = nuoc_sx,
                quyet_dinh        = quyet_dinh, 
                loai_thuoc        = loai_thuoc, 
                cong_bo           = cong_bo,
                loai_thau         = loai_thau,
                nhom_thau         = group_nhom_thau,
                cong_ty           = group_cong_ty,
                bao_hiem          = bao_hiem
            )

            bulk_create_data.append(model)

        Thuoc.objects.bulk_update_or_create(bulk_create_data, [
            'ma_hoat_chat', 
            'ten_hoat_chat', 
            'duong_dung', 
            'ham_luong', 
            'ten_thuoc', 
            'so_dang_ky', 
            'dong_goi', 
            'don_vi_tinh', 
            'don_gia', 
            'don_gia_tt',
            'so_luong_kha_dung',
            'ma_cskcb',
            'hang_sx',
            'nuoc_sx',
            'quyet_dinh',
            'cong_bo',
            'loai_thau',
            'nhom_thau'
        ], match_field = 'ma_thuoc')
        response = {
            'status': 200,
            'message': 'Import Thanh Cong'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def store_cong_ty(request):
    if request.method == 'POST':
        ten_cong_ty          = request.POST.get('ten_cong_ty')
        giay_phep_kinh_doanh = request.POST.get('giay_phep_kinh_doanh')
        so_lien_lac          = request.POST.get('so_lien_lac')
        email                = request.POST.get('email')
        dia_chi              = request.POST.get('dia_chi')

        CongTy.objects.get_or_create(
            ten_cong_ty          = ten_cong_ty,
            giay_phep_kinh_doanh = giay_phep_kinh_doanh,
            so_lien_lac          = so_lien_lac,
            email                = email,
            dia_chi              = dia_chi,
        )[0]

        response = {
            "message" : "Them Thanh Cong",
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def danh_sach_bai_dang(request):
    return render(request, "le_tan/danh_sach_bai_dang.html")

def store_thanh_toan_lam_sang(request):
    if request.method == 'POST':
        id_lich_hen = request.POST.get('id')
        gia_tien = request.POST.get('gia_tien')

        lich_hen = LichHenKham.objects.get(id = id_lich_hen)
        hoa_don_lam_sang = HoaDonLamSang.objects.create(
            gia_tien = gia_tien
        )
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0]
        lich_hen.trang_thai = trang_thai
        lich_hen.save()

        HoaDonTong.objects.get_or_create(hoa_don_lam_sang = hoa_don_lam_sang, lich_hen = lich_hen)[0]

        response = {
            'status': 200,
            'message': 'Thanh Toán Lâm Sàng Thành Công'
        }
        # return redirect('/danh_sach_benh_nhan/')
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def danh_sach_phong_chuc_nang(request):
    return render(request, 'le_tan/danh_sach_phong_chuc_nang.html')

def them_phong_chuc_nang(request):
    return render(request, 'le_tan/them_phong_chuc_nang.html')

def combine_pcn_dich_vu(request):
    if request.method == "POST":
        ten_phong_chuc_nang = request.POST.get("ten_phong_chuc_nang")
        request_data        = request.POST.get('data')
        data                = json.loads(request_data)
        
        print(ten_phong_chuc_nang)
        print(data)

        bulk_create_data = []
        for obj in data:
            id = obj['obj']['id']
            dich_vu_kham = DichVuKham.objects.get(id=id) 
            model = PhongChucNang(ten_phong_chuc_nang = ten_phong_chuc_nang, dich_vu_kham = dich_vu_kham)

            bulk_create_data.append(model)
        
        PhongChucNang.objects.bulk_create(bulk_create_data)
        response = {
            'status': 200,
            'message': 'Thêm Phòng Chức Năng Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def update_phong_chuc_nang(request, **kwargs):
    id_phong_chuc_nang = kwargs.get('id')
    instance = get_object_or_404(PhongChucNang, id=id_phong_chuc_nang)
    form = PhongChucNangForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_phong_chuc_nang': id_phong_chuc_nang,
    }
    return render(request, 'le_tan/update_phong_chuc_nang.html', context=data)

