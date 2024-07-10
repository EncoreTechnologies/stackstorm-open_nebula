# stackstorm-open_nebula
StackStorm integration pack for Open Nebula

This pack integrates with Open Nebula and allows for the creation and management of objects.

More detailed information about the XML-RPC API endpoints, XML schema, and parameters can be found here:
https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html

More details about the pyone wrapper can be found here:
https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/python.html

## Connection Configuration

You will need to specify the details of the Open Nebula instance you will be connecting to within
the `/opt/stackstorm/config/open_nebula.yaml` file.

Copy the example configuration in [open_nebula.yaml.example](./open_nebula.yaml.example)
to `/opt/stackstorm/configs/open_nebula.yaml` and edit as required.

If you only have a single Open Nebula environment then you can set it up as `default`, and you won't need to specify it when running actions, e.g.:

```yaml
---
ssl_verify: true
open_nebula:
  default:
    host: "myone.local"
    port: 2633
    user: "oneadmin"
    passwd: "******"
```

You can also specify multiple environments using nested values. To choose which one to use simply pass the name into the `ovirt` parameter of any action:

```yaml
---
ssl_verify:
open_nebula:
  dev:
    host:
    port:
    user:
    passwd:
  prod:
    host:
    port:
    user:
    passwd:
```

You can also include a default environment in a list as well and that will be used if nothing is passed in the action.

**Note** : When modifying the configuration in `/opt/stackstorm/configs/` please
           remember to tell StackStorm to load these new values by running
           `st2ctl reload --register-configs`

## Connection Options
The `action_base.yaml` file contains 2 methods to connect to the API. Both use the data from the config file above.
`pyone_session_create` a python wrapper that's good for creating and updating objects
More information: https://docs.opennebula.io/6.6/integration_and_development/system_interfaces/python.html
`xmlrpc_session_create` an xmlrpc connection that's good for returning readable data
More information on the XML-RPC API methods: https://docs.opennebula.io/6.6/integration_and_development/system_interfaces/api.html

## Actions
|  Action  |  Description  |
|---|---|
|  clusters_get  |  Retrieves information for all the clusters in the pool or the given clusters if any IDs are passed  |
|  datastores_get  |  Retrieves information for all or part of the datastores in the pool or the given datastores if any IDs are passed  |
|  hosts_get  |  Retrieves information for all the hosts in the pool or the given hosts if any IDs are passed  |
|  networks_get  |  Retrieves information for all or part of the virtual networks in the pool or the given virtual networks if any IDs are passed  |
|  template_attribute_get  |  Return the value of the given attribute from the template  |
|  template_attributes_update  | Update the dict of given attributes on the given template  |
|  template_clone  |  Clones an existing virtual machine template  |
|  template_delete  |  Deletes the given template from the pool  |
|  template_disks_get  |  Return a list of disks on the given template  |
|  template_get_by_name  |  Retrieves the given template by name on an Open Nebula system  |
|  template_instantiate  |  Instantiates a new virtual machine from a given template ID  |
|  templates_get  |  Retrieves information for all or part of the templates in the pool or the given templates if any IDs are passed  |
|  users_get  |  Retrieves information for all the users in the pool or the given users if any IDs are passed  |
|  vm_action_submit  |  Run the given onevm action on the given VM. Each onevm action that this can run also has it's own corresponding ST2 action in this pack  |
|  vm_attribute_get  |  Return the value of the given attribute from the VM  |
|  vm_attributes_update  |  Update the dict of given attributes on the given VM  |
|  vm_bestfit  |  Determine the best host and datastore to provision a new VM to on a given cluster  |
|  vm_disk_add  |  Adds a disk to a VM in Open Nebula  |
|  vm_get_by_name  |  Retrieves the given VM by name on an Open Nebula system  |
|  vm_hold  |  Sets the VM to hold state. The scheduler will not deploy VMs in the hold state  |
|  vm_labels_add  |  Append one or more labels to the given VM  |
|  vm_labels_get  |  Retrieves a list of labels on the given VM  |
|  vm_lock  |  Locks a VM from having actions performed on it  |
|  vm_poweroff  |  Gracefully powers off a running VM by sending the ACPI signal. It is similar to suspend but without saving the VM state  |
|  vm_reboot  |  Gracefully reboots a running VM, sending the ACPI signal  |
|  vm_release  |  Releases a VM from hold state, setting it to pending  |
|  vm_reschedule  |  Sets the reschedule flag for the VM. The Scheduler will migrate the VM in the next monitorization cycle to a Host that better matches the requirements and rank restrictions  |
|  vm_resize  |  Changes the capacity of CPU, VCPU, and/or MEMORY on the virtual machine  |
|  vm_resume  |  Resumes the execution of VMs in the stopped, suspended, undeployed and poweroff states  |
|  vm_snapshot_create  |  Create a snapshot of the given VM  |
|  vm_snapshot_delete_id  |  Delete a snapshot from the given VM from the ID  |
|  vm_snapshots_delete_age  |  Delete snapshots older than a given age  |
|  vm_snapshots_get  |  Return a list of snapshots on the given VM  |
|  vm_stop  |  Same as undeploy but also the VM state is saved to later resume it  |
|  vm_suspend  |  The VM state is saved in the running Host. When a suspended VM is resumed, it is immediately deployed in the same Host by restoring its saved state  |
|  vm_terminate  |  Gracefully shuts down and deletes a running VM, sending the ACPI signal  |
|  vm_undeploy  |  Gracefully shuts down and deletes a running VM, sending the ACPI signal  |
|  vm_unlock  |  Unocks a VM from a locked state  |
|  vm_unreschedule  |  Clears the reschedule flag for the VM, canceling the rescheduling operation  |
|  vms_get  |  Retrieves information for all or part of the VMs in the pool or the given VMs if any IDs are passed |
|  vms_get_ext  |  Retrieves extended information for all or part of the VMs in the pool or the given VMs if any IDs are passed |

## Example Commands
Update custom attributes on a VM: \
`st2 run open_nebula.vm_attributes_update vm_id="5" attributes='{"ATTR1": "VALUE1", "LABELS": "ST2,test_label,Label2"}'`
<br/><br/>
Update memory and CPU on a VM: \
`st2 run open_nebula.vm_resize vm_id="80" mem_mb="4096" vcpu_num="2"`
<br/><br/>
Power off a VM: \
`st2 run open_nebula.vm_poweroff vm_id="80"` \
or: \
`st2 run open_nebula.vm_action_submit vm_id="221" vm_action="poweroff"`
