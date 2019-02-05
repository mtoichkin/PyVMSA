import ssl
from django.core.management.base import BaseCommand
from pyVim.connect import SmartConnect, Disconnect
from cfg import ip_vm_host_list, vm_user, vm_pwd
from pyvmomi.models import *


class Command(BaseCommand):
    help = 'Capture DB'

    def handle(self, *args, **options):
        capture_db()


def connect_vm_host(vm_host, vm_user, vm_pwd):

    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE
    try:
        print("Host: {} Connect...".format(vm_host))
        service_instance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd)
        print('Host: {} Valid certificate'.format(vm_host))
    except ssl.SSLError:
        try:
            service_instance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd, sslContext=s)
            print('Host: {} Invalid or untrusted certificate'.format(vm_host))
        except:
            return print("Host:{} Invalid Login".format(vm_host))
    except:
        return print("Host: {} Connect failed".format(vm_host))
    return service_instance

def capture_db_host(vm_host, service_instance):
    try:
        db_host = Host()
        db_host.host_ip = vm_host

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

        db_host.host_fullname = service_instance.content.about.fullName
        db_host.host_ostype = service_instance.content.about.osType
        db_host.host_productlineid = service_instance.content.about.productLineId
        db_host.host_apiversion = service_instance.content.about.apiVersion

        for datacenter in service_instance.content.rootFolder.childEntity:

            for hostfolder in datacenter.hostFolder.childEntity:

                print("Host name: {}".format(hostfolder.name))

                db_host.host_name = hostfolder.name

                # vim.ComputeResource
                #
                # effectiveCpu:
                #   Effective CPU resources (in MHz) available to run virtual machines. This is the aggregated effective
                #  resource level from all running hosts. Hosts that are in maintenance mode or are unresponsive are not
                #  counted. Resources used by the VMware Service Console are not included in the aggregate. This value
                #  represents the amount of resources available for the root resource pool for running virtual machines.
                #
                # effectiveMemory:
                #   Effective memory resources (in MB) available to run virtual machines. This is the aggregated
                #  effective resource level from all running hosts. Hosts that are in maintenance mode or are
                #  unresponsive are not counted. Resources used by the VMware Service Console are not included in the
                #  aggregate. This value represents the amount of resources available for the root resource pool for
                #  running virtual machines.
                #
                # numCpuCores:
                #   Number of physical CPU cores. Physical CPU cores are the processors contained by a CPU package.
                #
                # numCpuThreads:
                #   Aggregated number of CPU threads.
                #
                # overallStatus:
                #   Overall alarm status. In releases after vSphere API 5.0, vSphere Servers might not generate property
                #  collector update notifications for this property. To obtain the latest value of the property, you can
                #  use PropertyCollector methods RetrievePropertiesEx or WaitForUpdatesEx. If you use the
                #  PropertyCollector.WaitForUpdatesEx method, specify an empty string for the version parameter. Since
                #  this property is on a DataObject, an update returned by WaitForUpdatesEx may contain values for this
                #  property when some other property on the DataObject changes. If this update is a result of a call to
                #  WaitForUpdatesEx with a non-empty version parameter, the value for this property may not be current.
                #
                # totalCpu:
                #   Aggregated CPU resources of all hosts, in MHz.
                #
                # totalMemory:
                #   Aggregated memory resources of all hosts, in bytes.
                #

                db_host.host_effectivecpu = int(hostfolder.summary.effectiveCpu)
                db_host.host_effectivememory = int(hostfolder.summary.effectiveMemory) / 1073741824
                db_host.host_numcpucores = hostfolder.summary.numCpuCores
                db_host.host_numcputhreads = int(hostfolder.summary.numCpuThreads)
                db_host.host_overallstatus = hostfolder.summary.overallStatus
                db_host.host_totalcpu = hostfolder.summary.totalCpu
                db_host.host_totalmemory = int(hostfolder.summary.totalMemory)/1073741824
                print("db_host.save")
                db_host.save()

    except type:
        print('failed  capture_db_host')
    return db_host

def capture_db_datacenter(db_host, service_instance):
    try:
        # Capture ESXi host Datastore
        # vim.Datastore
        #
        # vim.Datastore.Summary
        #
        # name:
        #   The name of the datastore.
        #
        # url:
        #   The unique locator for the datastore.
        #
        # capacity:
        #   Maximum capacity of this datastore, in bytes. This value is updated periodically by the server.
        #  It can be explicitly refreshed with the Refresh operation. This property is guaranteed to be valid
        #  only if accessible is true.
        #
        # freeSpace:
        #   Available space of this datastore, in bytes.
        #
        # type:
        #   Type of file system volume, such as VMFS or NFS.
        #

        for datacenter in service_instance.content.rootFolder.childEntity:

            for datastore in datacenter.datastoreFolder.childEntity:

                db_datastore = Datastore()
                db_datastore.host = db_host
                db_datastore.datastore = str(datastore.summary.datastore).replace('vim.Datastore:', '')
                db_datastore.name = datastore.summary.name
                db_datastore.url = datastore.summary.url
                db_datastore.capacity = int(datastore.summary.capacity)
                db_datastore.freespace = int(datastore.summary.freeSpace)
                db_datastore.type = datastore.summary.type
                print("db_datastore.save")
                db_datastore.save()

    except type:
        print('failed  capture_db_datacenter')
    return

def capture_db_network(db_host, service_instance):
    try:
        for datacenter in service_instance.content.rootFolder.childEntity:

            for hostfolder in datacenter.hostFolder.childEntity:

                for hostsystem in hostfolder.host:
                    host_vswitches = []
                    for vswitch in hostsystem.config.network.vswitch:

                        db_virtualswitch = Virtualswitch()
                        db_virtualswitch.host = db_host
                        db_virtualswitch.name = vswitch.name
                        db_virtualswitch.mtu = vswitch.mtu
                        print("db_virtualswitch.save")
                        db_virtualswitch.save()
                        print(db_virtualswitch.id)

                        vswitch_info = dict()
                        vswitch_pnics = []
                        vswitch_portgroups = []

                        for pnic in vswitch.pnic:
                            pnic = pnic.replace('key-vim.host.PhysicalNic-', '')
                            vswitch_pnics.append(pnic)
                        for portgroup in vswitch.portgroup:
                            portgroup = portgroup.replace('key-vim.host.PortGroup-', '')
                            vswitch_portgroups.append(portgroup)

                        vswitch_info.update(
                            {'id': db_virtualswitch.id,
                             'pnics': vswitch_pnics,
                             'portgroups': vswitch_portgroups})
        print(vswitch_info)
    except type:
        print('failed  capture_db_network')
    return

def capture_db():
    for vm_host in ip_vm_host_list:

        service_instance = connect_vm_host(vm_host, vm_user, vm_pwd)

        if service_instance is None:
            print("Host:{} skip".format(vm_host))
        else:
            db_host = capture_db_host(vm_host, service_instance)
            capture_db_datacenter(db_host, service_instance)
            capture_db_network(db_host, service_instance)

    print(db_host)
    Disconnect(service_instance)

    return print('Ok')

