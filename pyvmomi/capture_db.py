import os, ssl, django
from pyVim.connect import SmartConnect, Disconnect

from cfg import ip_vm_host_list, vm_user, vm_pwd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyvmsa.settings")
django.setup()
from pyvmomi.models import Host

def Connect_VM_Host(vm_host,vm_user,vm_pwd):
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE
    try:
        print("Host: {} Connect...".format(vm_host))
        ServiceInstance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd)
        print('Host: {} Valid certificate'.format(vm_host))
    except ssl.SSLError:
        try:
            ServiceInstance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd, sslContext=s)
            print('Host: {} Invalid or untrusted certificate'.format(vm_host))
        except:
            return print("Host:{} Invalid Login".format(vm_host))
    except:
        return print("Host: {} Connect failed".format(vm_host))
    return ServiceInstance

def Capture_DB_Host(vm_host, ServiceInstance):
    try:
        db_Host = Host()
        db_Host.host_ip = vm_host

        # vim.AboutInfo:
        #
        #  fullName:
        #   The complete product name, including the version information.
        #
        #  osType:
        #   Examples of values are:
        #     "win32-x86" - For x86-based Windows systems.
        #     "linux-x86" - For x86-based Linux systems.
        #     "vmnix-x86" - For the x86 ESX Server microkernel.
        #
        #  productLineId:
        #   Examples of values are:
        #     "gsx" - For the VMware Server product.
        #     "esx" - For the ESX product.
        #     "embeddedEsx" - For the ESXi product.
        #     "vpx" - For the VirtualCenter product.
        #
        #  apiVersion:
        #   The version of the API as a dot-separated string.
        #

        db_Host.host_fullname = ServiceInstance.content.about.fullName
        db_Host.host_ostype = ServiceInstance.content.about.osType
        db_Host.host_productlineid = ServiceInstance.content.about.productLineId
        db_Host.host_apiversion = ServiceInstance.content.about.apiVersion

        for datacenter in ServiceInstance.content.rootFolder.childEntity:

            for hostFolder in datacenter.hostFolder.childEntity:

                print("Host name: {}".format(hostFolder.name))

                db_Host.host_name = hostFolder.name

                # vim.ComputeResource
                #
                # effectiveCpu:
                #  Effective CPU resources (in MHz) available to run virtual machines. This is the aggregated effective
                # resource level from all running hosts. Hosts that are in maintenance mode or are unresponsive are not
                # counted. Resources used by the VMware Service Console are not included in the aggregate. This value
                # represents the amount of resources available for the root resource pool for running virtual machines.
                #
                # effectiveMemory:
                #  Effective memory resources (in MB) available to run virtual machines. This is the aggregated
                # effective resource level from all running hosts. Hosts that are in maintenance mode or are
                # unresponsive are not counted. Resources used by the VMware Service Console are not included in the
                # aggregate. This value represents the amount of resources available for the root resource pool for
                # running virtual machines.
                #
                # numCpuCores:
                #  Number of physical CPU cores. Physical CPU cores are the processors contained by a CPU package.
                #
                # numCpuThreads:
                #  Aggregated number of CPU threads.
                #
                # overallStatus:
                #  Overall alarm status. In releases after vSphere API 5.0, vSphere Servers might not generate property
                #  collector update notifications for this property. To obtain the latest value of the property, you can
                #  use PropertyCollector methods RetrievePropertiesEx or WaitForUpdatesEx. If you use the
                #  PropertyCollector.WaitForUpdatesEx method, specify an empty string for the version parameter. Since
                #  this property is on a DataObject, an update returned by WaitForUpdatesEx may contain values for this
                #  property when some other property on the DataObject changes. If this update is a result of a call to
                #  WaitForUpdatesEx with a non-empty version parameter, the value for this property may not be current.
                #
                # totalCpu:
                #  Aggregated CPU resources of all hosts, in MHz.
                #
                # totalMemory:
                #  Aggregated memory resources of all hosts, in bytes.
                #

                db_Host.host_effectivecpu = int(hostFolder.summary.effectiveCpu)
                db_Host.host_effectivememory = int(hostFolder.summary.effectiveMemory) / 1073741824
                db_Host.host_numcpucores = hostFolder.summary.numCpuCores
                db_Host.host_numcputhreads = int(hostFolder.summary.numCpuThreads)
                db_Host.host_overallstatus = hostFolder.summary.overallStatus

                db_Host.host_totalcpu = hostFolder.summary.totalCpu
                db_Host.host_totalmemory = int(hostFolder.summary.totalMemory)/1073741824


    except:
        print('failed  Capture_DB_Host')
    return db_Host.save()


def Capture_DB():
    for vm_host in ip_vm_host_list:

        service_instance = Connect_VM_Host(vm_host, vm_user, vm_pwd)

        if service_instance is None:
            print("Host:{} skip".format(vm_host))
        else:
            Capture_DB_Host(vm_host, service_instance)

    Disconnect(service_instance)

    return print('Ok')

Capture_DB()