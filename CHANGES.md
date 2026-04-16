## 1.2.1
- Added action template_image_datastore_get that retrieves the images on a template and returns the datastore(s) they are on 

## 1.2.0
- Added action templates_object_backup to save a copy of all or a subset of templates to the given directory
- Added action template_sched_req_update to update the SCHED_REQUIREMENTS and/or SCHED_DS_REQUIREMENTS of Open Nebula templates

## 1.1.9
- Updated vm_bestfit action to select least utilized host based on memory rather than VM count
- Updated get_by_name actions to handle edge cases where names have whitespace in Open Nebula

## 1.1.8
- Added action to test python connection with given credentials

## 1.1.7
- Added action to get list of VMs with given label

## 1.1.6
- Adds hypervisor type to data get action

## 1.1.5
- Adds wilds to data get action

## 1.1.4
- Fixed CI tests

## 1.1.3
- Added actions for looking up attributes on datastores

## 1.1.2
- Updates data get actions and tests to parse zone names to csv

## 1.1.1
- Updated files to fix flake8 errors
- Fixed params for vm terminate action

## 1.1.0
- Added unit tests for all python actions

## 1.0.2
- Updates bus type on windows vms for vm disk add action

## 1.0.1
- Added action to check an attribute for a list of vms

## 1.0.0

- Initial release
- Added pack files and base action
- Added the following actions:
  - vms_list - Retrieves the vms on an Open Nebula system
