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
      - hostname: 'hana01'

NUREMBERG:
  hana.sr_primary_enabled:
    - sid: 'prd'
    - inst: '00'
    - password: 'Qwerty1234'
    - cleanup: true
    - backup:
      - user: 'backupkey'
      - password:  'Qwerty1234'
      - database: 'SYSTEMDB'
      - file: 'backup'
    - userkey:
      - key: 'backupkey'
      - environment: 'hana01:30013'
      - user: 'SYSTEM'
      - password: 'Qwerty1234'
      - database: 'SYSTEMDB'
    - require:
      - hana-install
