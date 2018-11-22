NUREMBERG:
    hana.sr_primary_enabled:
      - sid: 'prd'
      - inst: '00'
      - password: 'Qwerty1234'
      - cleanup: true
      - backup:
        - user: 'backupkey'
        - password:  Qwerty1234
        - database: 'SYSTEMDB'
        - file: 'backup'
      - userkey:
        - key: 'backupkey'
        - environment: 'hana01:30013'
        - user: 'SYSTEM'
        - password: 'Qwerty1234'
        - database: 'SYSTEMDB'
