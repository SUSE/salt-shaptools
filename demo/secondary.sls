primary-available:
  cmd.run:
    - name: until nc -z hana01 40002; do sleep 1; done
    - timeout: 60

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
