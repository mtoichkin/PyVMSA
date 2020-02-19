from django.core import management
from django.shortcuts import render, get_object_or_404
from .models import Host, Virtualmachine
from django.utils import timezone
from django.db.models import Max, Q, OuterRef, Subquery


# Create your views here.
def machine_list(request):
    if request.method == "POST":
        management.call_command('capture_db')
    sq = Host.objects.filter(host_ip=OuterRef('host_ip')).order_by('-created_date')  # deferred execution
    hosts = Host.objects.filter(pk=Subquery(sq.values('pk')[:1]))
    return render(request, 'pyvmomi/machine_list.html', {'hosts': hosts})


def machine_detail(request, pk):
    machine = get_object_or_404(Virtualmachine, pk=pk)
    return render(request, 'pyvmomi/machine_detail.html', {'machine': machine})


'''def host_new(request):
    if request.method == "POST":
        #form = HostForm(request.POST)
        #if form.is_valid():
        management.call_command('capture_db')
    return render(request, 'pyvmomi/machine_list.html')'''

