hana-install:
  hana.installed:
    - root_user: 'root'
    - root_password: 's'
    - software_path: '/root/sap_inst/51052481'
    - sid: 'prd'
    - inst: '00'
    - password: 'Qwerty1234'
    - system_user_password: 'Qwerty1234'
    - extra_parameters:
      - hostname: 'hana02'

primary-available:
  cmd.run:
    - name: until nc -z hana01 40002; do sleep 1; done
    - timeout: 60
    - require:
      - hana-install

PRAGUE:
  hana.sr_secondary_registered:
    - remote_host: hana01
    - remote_instance: '00'
    - replication_mode: sync
    - operation_mode: logreplay
    - sid: 'prd'
    - inst: '00'
    - password: 'Qwerty1234'
    - cleanup: true
    - require:
      - primary-available
