from django.db import models
from django.utils import timezone


# Create your models here.
class Host(models.Model):
    host_ip = models.CharField(max_length=200, default='')
    host_fullname = models.CharField(max_length=100, default='')
    host_ostype = models.CharField(max_length=100, default='')
    host_productlineid = models.CharField(max_length=100, default='')
    host_apiversion = models.CharField(max_length=50, default='')
    host_name = models.CharField(max_length=100, default='')
    host_totalcpu = models.PositiveIntegerField(default=0)
    host_numcpucores = models.PositiveIntegerField(default=0)
    host_numcputhreads = models.PositiveIntegerField(default=0)
    host_effectivecpu = models.PositiveIntegerField(default=0)
    host_totalmemory = models.PositiveIntegerField(default=0)
    host_effectivememory = models.PositiveIntegerField(default=0)
    host_overallstatus = models.CharField(max_length=50, default='')
    created_date = models.DateTimeField(
            default=timezone.now)

    '''def publish(self):
        self.created_date = timezone.now()
        self.save()'''

    def __str__(self):
        return self.host_ip


class Virtualswitch(models.Model):
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='')
    mtu = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Datastore(models.Model):
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    datastore = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    freespace = models.PositiveIntegerField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Virtualmachine(models.Model):
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='N/A')
    toolsStatus = models.CharField(max_length=100, default='N/A')
    guestFullName = models.CharField(max_length=200, default='N/A')
    hostName = models.CharField(max_length=100, default='N/A')
    guestState = models.CharField(max_length=50, default='N/A')
    ipAddress = models.CharField(max_length=100, default='N/A')
    numcpu = models.PositiveIntegerField(default=0)
    numcorepersocket = models.PositiveIntegerField(default=0)
    memorymb = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Storage(models.Model):
    virtualmachine = models.ForeignKey(Virtualmachine, on_delete=models.CASCADE)
    datastore = models.CharField(max_length=150, default='N/A')
    committed = models.BigIntegerField(default=0)
    uncommitted = models.BigIntegerField(default=0)
    unshared = models.BigIntegerField(default=0)


class Disk(models.Model):
    virtualmachine = models.ForeignKey('Virtualmachine', on_delete=models.CASCADE)
    diskpath = models.CharField(max_length=100, default='N/A')
    capacity = models.BigIntegerField()
    freespace = models.BigIntegerField()

    def __str__(self):
        return self.discpath


class Route(models.Model):
    virtualmachine = models.ForeignKey('Virtualmachine', on_delete=models.CASCADE)
    iproute = models.CharField(max_length=100, default='N/A')
    gateway = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.iproute


class Physicalnick(models.Model):
    virtualswitch = models.ForeignKey('Virtualswitch', on_delete=models.CASCADE)
    device = models.CharField(max_length=100, default='N/A')
    driver = models.CharField(max_length=100, default='N/A')
    mac = models.CharField(max_length=100, default='N/A')
    speedmb = models.CharField(max_length=100, default='N/A')
    duplex = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.device


class Portgroup(models.Model):
    virtualswitch = models.ForeignKey('Virtualswitch', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='N/A')
    vlanid = models.PositiveIntegerField()
    device = models.CharField(max_length=100, default='N/A')
    dhcp = models.CharField(max_length=100, default='N/A')
    ipaddress = models.CharField(max_length=100, default='N/A')
    subnetmask = models.CharField(max_length=100, default='N/A')
    mac = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.name



