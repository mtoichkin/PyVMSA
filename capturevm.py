from pyVim.connect import SmartConnect, Disconnect
import ssl
from cfg import ip_vm_host_list, vm_user, vm_pwd



def Connect_VM_Host(vm_host,vm_user,vm_pwd):
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE
    try:
        print("Host:{} Connect...".format(vm_host))
        ServiceInstance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd)
        print('Host:{} Valid certificate'.format(vm_host))
    except ssl.SSLError:
        try:
            ServiceInstance = SmartConnect(host=vm_host, user=vm_user, pwd=vm_pwd, sslContext=s)
            print('Host:{} Invalid or untrusted certificate'.format(vm_host))
        except:
            return print("Host:{} Invalid Login".format(vm_host))
    except:
        return print("Host:{} Connect failed".format(vm_host))
    return ServiceInstance

def Capture_ServiceInstance(ServiceInstance):
    # vim.AboutInfo:
    #  fullName:
    #  The complete product name, including the version information.
    #  osType:
    #  Examples of values are:
    #     "win32-x86" - For x86-based Windows systems.
    #     "linux-x86" - For x86-based Linux systems.
    #     "vmnix-x86" - For the x86 ESX Server microkernel.
    #  productLineId:
    #  Examples of values are:
    #     "gsx" - For the VMware Server product.
    #     "esx" - For the ESX product.
    #     "embeddedEsx" - For the ESXi product.
    #     "vpx" - For the VirtualCenter product.
    #  apiVersion:
    #  The version of the API as a dot-separated string.
    try:
        si_info = dict()
        si_info.update(
            {'fullName': ServiceInstance.content.about.fullName,
             'osType': ServiceInstance.content.about.osType,
             'productLineId': ServiceInstance.content.about.productLineId,
             'apiVersion': ServiceInstance.content.about.apiVersion})
    except:
        print('failed get vim.AboutInfo')
    return si_info

def Capture_ComputeResource(ComputeResource):
    # vim.ComputeResource.Summary
    try:
        cr_info = dict()
        cr_info.update(
            {'name': ComputeResource.name,
             'totalCpu':  int(ComputeResource.summary.totalCpu), #//int(ComputeResource.summary.numCpuCores)),
             'numCpuCores': int(ComputeResource.summary.numCpuCores),
             'numCpuThreads': int(ComputeResource.summary.numCpuThreads),
             'effectiveCpu': int(ComputeResource.summary.effectiveCpu),
             'totalMemory': int(ComputeResource.summary.totalMemory), #// 1073741824,
             'effectiveMemory': int(ComputeResource.summary.effectiveMemory), #// 1073741824,
             'overallStatus': ComputeResource.summary.overallStatus})

    except:
        print('failed get vim.ComputeResource.Summary')
    return cr_info

def Capture_Network(host):
    net_info = dict()

    net_info.update(
        {# vim.host.PhysicalNic
         'PhysicalNic': Capture_Network_PhysicalNic(host),
         # vim.host.VirtualNic
         'VirtualNic': Capture_Network_VirtualNic(host),
         # vim.host.PortGroup
         'PortGroup': Capture_Network_PortGroup(host),
         # vim.host.VirtualSwitch
         'VirtualSwitch': Capture_Network_VirtualSwitch(host)})
    return net_info

def Capture_Network_PhysicalNic(host):
    # Capture ESXi host physical nics
    host_pnics = []
    for pnic in host.config.network.pnic:
        pnic_info = dict()
        pnic_info.update(
            {'device': pnic.device,
             'driver': pnic.driver,
             'mac': pnic.mac})
        # Capture linkSpeed
        try:
            if pnic.spec.linkSpeed is not None:
                pnic_info.update(
                    {'speedMb': pnic.spec.linkSpeed.speedMb,
                     'duplex': pnic.spec.linkSpeed.duplex})
            else:
                pnic_info.update(
                    {'speedMb': 'unset',
                     'duplex': 'unset'})
        except:
            print('failed get pnic.spec.linkSpeed')

        host_pnics.append(pnic_info)
    return host_pnics

def Capture_Network_VirtualNic(host):
    # Capture ESXi host virtual nics
    host_vnics = []
    for vnic in host.config.network.vnic:
        vnic_info = dict()
        vnic_info.update(
            {'device': vnic.device,
             'portgroup': vnic.portgroup,
             'dhcp': vnic.spec.ip.dhcp,
             'ipAddress': vnic.spec.ip.ipAddress,
             'subnetMask': vnic.spec.ip.subnetMask,
             'mac': vnic.spec.mac,
             'mtu': vnic.spec.mtu})
        host_vnics.append(vnic_info)
    return host_vnics

def Capture_Network_PortGroup(host):
    # Capture ESXi host port group
    host_portgroup = []
    for portgroup in host.config.network.portgroup:
        portgroup_info = dict()
        portgroup_info.update(
            {'name': portgroup.spec.name,
             'vlanId': portgroup.spec.vlanId,
             'vswitchName': portgroup.spec.vswitchName})
        host_portgroup.append(portgroup_info)
    return host_portgroup

def Capture_Network_VirtualSwitch(host):
    # Capture ESXi host virtual switches
    host_vswitches = []
    for vswitch in host.config.network.vswitch:
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
            {'name': vswitch.name,
             'pnics': vswitch_pnics,
             'portgroups': vswitch_portgroups,
             'mtu': vswitch.mtu})
        host_vswitches.append(vswitch_info)
    return host_vswitches

def Capture_Datastore(host):
    # Capture ESXi host Datastore
    # vim.Datastore
    host_datastore = []
    for datastore in host.datastoreFolder.childEntity:
        datastore_info = dict()
        #print(datastore.info)
        #print(datastore.capability)
        #print(datastore.summary)
        #print(dir(datastore))
        datastore_info.update(
            #vim.Datastore.Summary
            # name
            # The name of the datastore.
            # url
            # The unique locator for the datastore.
            # capacity
            # Maximum capacity of this datastore, in bytes. This value is updated periodically by the server.
            # It can be explicitly refreshed with the Refresh operation. This property is guaranteed to be valid
            # only if accessible is true.
            # freeSpace
            # Available space of this datastore, in bytes.
            # type
            # Type of file system volume, such as VMFS or NFS.
            {'datastore': datastore.summary.datastore,
             'name': datastore.summary.name,
             'url': datastore.summary.url,
             'capacity': int(datastore.summary.capacity),
             'freeSpace': int(datastore.summary.freeSpace),
             'type': datastore.summary.type})
        host_datastore.append(datastore_info)
    return host_datastore

def Capture_VirtualMachine(host):
    # Capture ESXi host VirtualMachine
    # vim.VirtualMachine
    host_virtualmachine = []
    for vm in host.vmFolder.childEntity:
        virtualmachine_info = dict()
        # vim.VirtualMachine
        virtualmachine_info.update(
            {'name': vm.name,
             # vim.vm.storage
             'storage': Capture_VirtualMachine_storage(vm),
             # vim.vm.GuestInfo
             'GuestInfo': Capture_VirtualMachine_GuestInfo(vm),
             # vim.vm.ConfigInfo
             'ConfigInfo': Capture_VirtualMachine_ConfigInfo(vm)})
        #print(dir(vm))
        #print(vm.runtime)
        #print(vm.summary)
        host_virtualmachine.append(virtualmachine_info)
    return host_virtualmachine

def Capture_VirtualMachine_storage(vm):
    # Capture VirtualMachine storage
    # vm.storage
    vm_storage = []
    # vm.storage.perDatastoreUsage
    for storage in vm.storage.perDatastoreUsage:
        storage_info = dict()
        storage_info.update(
            {'datastore': storage.datastore,
             'committed': storage.committed,
             'uncommitted': storage.uncommitted,
             'unshared': storage.unshared})
        vm_storage.append(storage_info)
    return vm_storage

def Capture_VirtualMachine_GuestInfo(vm):
    # Capture VirtualMachine GuestInfo
    # vim.vm.GuestInfo
    guestinfo_info = dict()
    # vim.vm.GuestInfo.DiskInfo
    vm_disk = []
    for disk in vm.guest.disk:
        vm_disk_info = dict()
        vm_disk_info.update(
            {'diskPath': disk.diskPath,
             'capacity': disk.capacity,
             'freeSpace': disk.freeSpace})
        vm_disk.append(vm_disk_info)


    guestinfo_info.update(
        {'toolsStatus': vm.guest.toolsStatus,
         'guestFullName': vm.guest.guestFullName,
         'hostName': vm.guest.hostName,
         'guestState': vm.guest.guestState,
         'ipAddress': vm.guest.ipAddress,
         'disk': vm_disk,
         # vim.vm.GuestInfo.NicInfo
         'ip': Capture_VirtualMachine_GuestInfo_net(vm),
         #vim.vm.GuestInfo.ipStack
         'route': Capture_VirtualMachine_GuestInfo_ipStack(vm)})
    return guestinfo_info

def Capture_VirtualMachine_GuestInfo_net(vm):
    # vim.vm.GuestInfo.NicInfo
    try:
        ipaddress = []
        for net in vm.guest.net:
                for ip in net.ipConfig.ipAddress:
                    ipaddress.append(str(ip.ipAddress) + '/' + str(ip.prefixLength))
    except:
        ipaddress = ['unset']
        return ipaddress
    return ipaddress

def Capture_VirtualMachine_GuestInfo_ipStack(vm):
    #vim.vm.GuestInfo.ipStack
    try:
        iproute = []
        for route in vm.guest.ipStack:
            for ip in route.ipRouteConfig.ipRoute:
                iproute_info = dict()
                iproute_info.update(
                    {'ip_route': str(ip.network)+'/'+str(ip.prefixLength),
                     'gateway': ip.gateway.ipAddress})
                iproute.append(iproute_info)
    except:
        iproute = ['unset']
        return iproute
    return iproute

def Capture_VirtualMachine_ConfigInfo(vm):
    # Capture VirtualMachine ConfigInfo
    # vim.vm.ConfigInfo
    config_info = dict()
    config_info.update(
        {#vim.vm.ConfigInfo
         #vim.vm.VirtualHardware
         'numCPU': vm.config.hardware.numCPU,
         'numCoresPerSocket': vm.config.hardware.numCoresPerSocket,
         'memoryMB': vm.config.hardware.memoryMB})
    return config_info

def main():
    capture_host_info = []
    for vm_host in ip_vm_host_list:
        print(vm_host)

        capture_vm_host_info = dict()

        capture_vm_host_info.update({'HOST IP': vm_host})

        ServiceInstance = Connect_VM_Host(vm_host, vm_user, vm_pwd)

        ## ServiceInstance

        if ServiceInstance is None:
            capture_host_info.append(capture_vm_host_info)
        else:
            capture_vm_host_info.update(
                {'vim.AboutInfo': Capture_ServiceInstance(ServiceInstance)})

            ## Datacenter

            for datacenter in ServiceInstance.content.rootFolder.childEntity:
                ## print(datacenter.hostFolder.childEntity)
                ## print(dir(datacenter))

                # vim.Datastore
                capture_vm_host_info.update({'vim.Datastore': Capture_Datastore(datacenter)})

                # vim.VirtualMachine
                capture_vm_host_info.update({'vim.VirtualMachine': Capture_VirtualMachine(datacenter)})

                # hostFolder
                for hostFolder in datacenter.hostFolder.childEntity:
                    # vim.ComputeResource

                    print("HOST", hostFolder.name)
                    capture_vm_host_info.update({'vim.ComputeResource': Capture_ComputeResource(hostFolder)})

                    for HostSystem in hostFolder.host:
                    # vim.HostSystem

                       ## print(HostSystem)
                       ## print(host.config.storageDevice)
                       ## print(dir(HostSystem.config))
                        capture_vm_host_info.update({'Network': Capture_Network(HostSystem)})

                #for networkFolder in datacenter.networkFolder.childEntity:
                    # vim.Network




            capture_host_info.append(capture_vm_host_info)

            Disconnect(ServiceInstance)

    return capture_host_info


print(main())
