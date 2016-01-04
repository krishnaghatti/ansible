import sys, getopt
from pysphere import *
from pysphere.resources import VimService_services as VI
from pysphere.vi_task import VITask

#sys.argv
#Connecting to the VCenter server.
server = VIServer()
#sys.argv[1]
server.connect("192.168.1.1", "administrator@vsphere.local", str(sys.argv[1]))
target_vm = "test_vm"

#Getting the VM based on the name. Target can be specified with the path to the VM in datastore like below.
#vm = server.get_vm_by_path("[datastore] path/to/file.vmx")
vm_obj = server.get_vm_by_name(target_vm)
#IP address of the VM.
ipAddress = "192.168.1.200"
#Hostname to be given to the VM.
hostName = "cento61"
domain_name = "mydomail.local"
netmask = '255.255.255.0'

vm_obj.power_off()
# Customize hostname and IP address
request = VI.CustomizeVM_TaskRequestMsg()
_this = request.new__this(vm_obj._mor)
_this.set_attribute_type(vm_obj._mor.get_attribute_type())
request.set_element__this(_this)
spec = request.new_spec()
globalIPSettings = spec.new_globalIPSettings()
spec.set_element_globalIPSettings(globalIPSettings)
# NIC settings, I used static ip, but it is able to set DHCP here.
nicSetting = spec.new_nicSettingMap()
adapter = nicSetting.new_adapter()
fixedip = VI.ns0.CustomizationFixedIp_Def("ipAddress").pyclass()
fixedip.set_element_ipAddress(ipAddress)
adapter.set_element_ip(fixedip)
adapter.set_element_subnetMask(netmask)
nicSetting.set_element_adapter(adapter)
spec.set_element_nicSettingMap([nicSetting,])
identity = VI.ns0.CustomizationLinuxPrep_Def("identity").pyclass()
identity.set_element_domain("domain_name")
hostName = VI.ns0.CustomizationFixedName_Def("hostName").pyclass()
hostName.set_element_name(target_vm.replace("_", ""))
identity.set_element_hostName(hostName)
spec.set_element_identity(identity)
request.set_element_spec(spec)
task = server._proxy.CustomizeVM_Task(request)._returnval

#Configuration status report.
vi_task = VITask(task, server)
status = vi_task.wait_for_state([vi_task.STATE_SUCCESS, vi_task.STATE_ERROR])
if status == vi_task.STATE_SUCCESS:
    print "VM successfully reconfigured"
elif status == vi_task.STATE_ERROR:
    print "Error reconfiguring vm:", vi_task.get_error_message()

#Powering the VM for reconfiguration.
vm_obj.power_on()
#Disconnect from the VCenter server
server.disconnect()
