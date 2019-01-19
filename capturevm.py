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
             'totalCpu':  int(ComputeResource.summary.totalCpu//int(ComputeResource.summary.numCpuCores)),
             'numCpuCores': int(ComputeResource.summary.numCpuCores),
             'numCpuThreads': int(ComputeResource.summary.numCpuThreads),
             'effectiveCpu': int(ComputeResource.summary.effectiveCpu),
             'totalMemory': float(ComputeResource.summary.totalMemory) // 1073741824,
             'effectiveMemory': float(ComputeResource.summary.effectiveMemory) // 1073741824,
             'overallStatus': ComputeResource.summary.overallStatus})

    except:
        print('failed get vim.ComputeResource.Summary')
    return cr_info

def Capture_Network(host):
    net_info = dict()
    # vim.host.PhysicalNic
    net_info.update({'PhysicalNic': Capture_Network_PhysicalNic(host)})
    # vim.host.VirtualNic
    net_info.update({'VirtualNic': Capture_Network_VirtualNic(host)})
    # vim.host.PortGroup
    net_info.update({'PortGroup': Capture_Network_PortGroup(host)})
    # vim.host.VirtualSwitch
    net_info.update({'PortGroup': Capture_Network_VirtualSwitch(host)})
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
                print(datacenter)

                #hostFolder

                for computeresource in datacenter.hostFolder.childEntity:
                    print("HOST", computeresource.name)
                    capture_vm_host_info.update({'vim.ComputeResource': Capture_ComputeResource(computeresource)})

                    for host in computeresource.host:
                        print(host)
                        print(host.config.storageDevice)
                        print(dir(host.config))
                        capture_vm_host_info.update({'Network': Capture_Network(host)})

            capture_host_info.append(capture_vm_host_info)

            Disconnect(ServiceInstance)

    return capture_host_info


print(main())
