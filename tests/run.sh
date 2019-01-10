cp salt/modules/*.py ../salt/salt/modules/
cp salt/states/*.py ../salt/salt/states/
cp tests/unit/modules/*.py ../salt/tests/unit/modules/
cp tests/unit/states/*.py ../salt/tests/unit/states/
py.test ../salt/tests/unit/modules/test_hanamod.py ../salt/tests/unit/states/test_hanamod.py -vv --cov=salt.modules.hanamod --cov=salt.states.hanamod --cov-config .coveragerc --cov-report term
py.test ../salt/tests/unit/modules/test_crmshmod.py ../salt/tests/unit/states/test_crmshmod.py -vv --cov=salt.modules.crmshmod --cov=salt.states.crmshmod --cov-config .coveragerc --cov-report term
