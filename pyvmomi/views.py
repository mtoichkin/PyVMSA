from django.shortcuts import render
from .models import Host
from django.utils import timezone


# Create your views here.
def machine_list(request):
    hosts = Host.objects.filter(created_date__lte=timezone.now()).order_by('created_date')
    return render(request, 'pyvmomi/machine_list.html', {'hosts': hosts})
