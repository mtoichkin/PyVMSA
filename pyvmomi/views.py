from django.shortcuts import render, get_object_or_404
from .models import Host, Virtualmachine
from django.utils import timezone


# Create your views here.
def machine_list(request):
    hosts = Host.objects.filter(created_date__lte=timezone.now()).order_by('created_date')
    return render(request, 'pyvmomi/machine_list.html', {'hosts': hosts})


def machine_detail(request, pk):
    machine = get_object_or_404(Virtualmachine, pk=pk)
    return render(request, 'pyvmomi/machine_detail.html', {'machine': machine})


