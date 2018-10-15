#!/usr/bin/python
# Copyright: Rubrik
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: rubrik_assign_physical_host_fileset
short_description: Assign a Rubrik fileset to a Linux or Windows machine.
description:
    - Assign a fileset to a Linux or Windows machine. If you have multiple filesets with identical names, you will 
      need to populate the filesets properties (i.e this functions keyword arguments) to find a specific match. 
      Filesets with identical names and properties are not supported.
version_added: '2.7'
author: 'Rubrik Ranger Team'
options:

  hostname:
    description:
      - The hostname or IP Address of the physical host you wish to associate to the Fileset.
    required: true
    aliases: ip_address
    type: str

  fileset_name:
    description:
      - The name of the Fileset you wish to assign to the Linux or Windows host.
    required: true
    type: str

  sla_name:
    description:
      - The name of the Fileset you wish to assign to the Linux or Windows host.
    required: true
    aliases: sla
    type: str

  operating_system:
    description:
      - The operating system of the physical host you are assigning a Fileset to.
    required: true
    choices: ['Linux', 'Windows']
    type: str

  include:
    description:
      - The full paths or wildcards that define the objects to include in the Fileset backup (ex: ['/usr/local', '*.pdf']).
    required: False
    default: []
    type: list

  exclude:
    description:
      - The full paths or wildcards that define the objects to exclude from the Fileset backup (ex: ['/user/local/temp', '.mov', '.mp3']).
    required: False
    default: []
    type: list

  exclude_exception:
    description:
      - The full paths or wildcards that define the objects that are exempt from the excludes variables. (ex: ['/company/*.mp4']).
    required: False
    default: []
    type: list

  follow_network_shares:
    description:
      - Include or exclude locally-mounted remote file systems from backups.
    required: False
    default: False
    type: bool

  backup_hidden_folders:
    description:
      - Include or exclude hidden folders inside locally-mounted remote file systems from backups.
    required: False
    default: False
    type: bool

 timeout:
    description:
      - The number of seconds to wait to establish a connection the Rubrik cluster before returning a timeout error.
    required: False
    default: 30
    type: int

extends_documentation_fragment:
    - rubrik_cdm
requirements: [rubrik_cdm]
'''

EXAMPLES = '''
- rubrik_assign_physical_host_fileset:
    hostname: 'python-physical-demo'
    fileset_name: 'Python SDK'
    sla_name: 'Gold'
    operating_system: 'Linux'
    include: ['/usr/local', '*.pdf']
    exclude: ['/user/local/temp', '.mov', '.mp3']
    exclude_exception: ['/company/*.mp4']
    follow_network_shares: true
    backup_hidden_folders: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.rubrikcdm import sdk_validation, connect, load_provider_variables, rubrik_argument_spec


def main():
    """ Main entry point for Ansible module execution.
    """

    argument_spec = rubrik_argument_spec

    argument_spec.update(
        dict(
            hostname=dict(required=True, type='str', aliases=['ip_address']),
            fileset_name=dict(required=True, type='str'),
            sla_name=dict(required=True, type='str', aliases=['sla']),
            operating_system=dict(required=True, type='str', choices=['Linux', 'Windows']),
            include=dict(required=False, type='list', default=[]),
            exclude=dict(required=False, type='list', default=[]),
            exclude_exception=dict(required=False, type='list', default=[]),
            follow_network_shares=dict(required=False, type='bool', default=False),
            backup_hidden_folders=dict(required=False, type='bool', default=False),
            timeout=dict(required=False, type='int', default=30),

        )
    )

    required_together = [
        ["include", "exclude", "exclude_exception", "follow_network_shares", "backup_hidden_folders"]
    ]

    module = AnsibleModule(argument_spec=argument_spec, required_together=required_together, supports_check_mode=False)

    sdk_present, rubrik_cdm = sdk_validation()

    if sdk_present is False:
        module.fail_json(msg="The Rubrik Python SDK is required for this module (pip install rubrik_cdm).")

    results = {}

    load_provider_variables(module)
    ansible = module.params

    rubrik = connect(rubrik_cdm, module)
    if isinstance(rubrik, str):
        module.fail_json(msg=rubrik)

    # If there are multiple Filesets on the cluster with the same name the end use will need to provide more specific information. That only occurs when includes != None
    if bool(ansible['include']) is False:

        try:
            api_request = rubrik.assign_physical_host_fileset(
                ansible['hostname'], ansible['fileset_name'], ansible['operating_system'], ansible['sla_name'], timeout=ansible["timeout"])
        except SystemExit as error:
            module.fail_json(msg=str(error))

    else:

        try:
            api_request = rubrik.assign_physical_host_fileset(ansible['hostname'], ansible['fileset_name'], ansible['operating_system'], ansible['sla_name'], ansible[
                "include"], ansible["exclude"], ansible["exclude_exception"], ansible["follow_network_shares"], ansible["backup_hidden_folders"], ansible["timeout"])
        except SystemExit as error:
            module.fail_json(msg=str(error))

    if "No change required" in api_request:
        results["changed"] = False
    else:
        results["changed"] = True

    results["response"] = api_request

    results["response"] = api_request

    module.exit_json(**results)


if __name__ == '__main__':
    main()
