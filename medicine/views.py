from django.shortcuts import render
from django.views import View

def ke_don_thuoc_view(request, **kwargs):
    user_id = kwargs.get('user_id')
    data = {
        'user_id': user_id
    }
    return render(request, 'bac_si_lam_sang/ke_don_thuoc.html', context=data)