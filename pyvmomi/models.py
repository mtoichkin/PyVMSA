from django.db import models
from django.utils import timezone


# Create your models here.
class Host(models.Model):
    host_ip = models.CharField(max_length=200)
    host_fullname = models.CharField(max_length=100)
    host_ostype = models.CharField(max_length=100)
    host_productlineid = models.CharField(max_length=100)
    host_apiversion = models.CharField(max_length=50)
    host_name = models.CharField(max_length=100)
    host_totalcpu = models.PositiveIntegerField()
    host_numcpucores = models.PositiveIntegerField()
    host_numcputhreads = models.PositiveIntegerField()
    host_effectivecpu = models.PositiveIntegerField()
    host_totalmemory = models.PositiveIntegerField()
    host_effectivememory = models.PositiveIntegerField()
    host_overallstatus = models.CharField(max_length=50)
    created_date = models.DateTimeField(
            default=timezone.now)

    '''def publish(self):
        self.created_date = timezone.now()
        self.save()'''

    def __str__(self):
        return self.host_ip


class Virtualswitch(models.Model):
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
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
    datastore = models.ManyToManyField('Datastore')
    name = models.CharField(max_length=100)
    numcpu = models.PositiveIntegerField()
    numcorepersocket = models.PositiveIntegerField()
    memorymb = models.PositiveIntegerField()

    def __str__(self):
        return self.name





