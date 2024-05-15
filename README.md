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
|  templates_get  |  Retrieves information for all or part of the templates in the pool or the given templates if any IDs are passed  |
|  users_get  |  Retrieves information for all the users in the pool or the given users if any IDs are passed  |
|  vm_attribute_get  |  Return the value of the given attribute from the VM  |
|  vm_attribute_update  |  Update the dict of given attributes on the given VM  |
|  vm_labels_add  |  Append one or more labels to the given VM  |
|  vm_labels_get  |  Retrieves a list of labels on the given VM  |
|  vm_resize  |  Changes the capacity of CPU, VCPU, and/or MEMORY on the virtual machine  |
|  vm_snapshot_create  |  Create a snapshot of the given VM  |
|  vm_snapshot_delete_id  |  Delete a snapshot from the given VM from the ID  |
|  vm_snapshots_delete_age  |  Delete snapshots older than a given age  |
|  vm_snapshots_get  |  Return a list of snapshots on the given VM  |
|  vms_get  |  Retrieves information for all or part of the VMs in the pool or the given VMs if any IDs are passed |
|  vms_get_ext  |  Retrieves extended information for all or part of the VMs in the pool or the given VMs if any IDs are passed |

## Example Commands
`st2 run open_nebula.vm_attribute_update vm_id="5" attributes='{"ATTR1": "VALUE1", "LABELS": "ST2,test_label,Label2"}'`
`st2 run open_nebula.vm_resize vm_id="80" mem_mb="4096" vcpu_num="2"`

