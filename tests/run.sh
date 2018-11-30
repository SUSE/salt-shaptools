cp salt/modules/*.py ../salt/salt/modules/
cp salt/states/*.py ../salt/salt/states/
cp tests/unit/modules/*.py ../salt/tests/unit/modules/
cp tests/unit/states/*.py ../salt/tests/unit/states/
../salt/tests/runtests.py -v -n unit.modules.test_hanamod
../salt/tests/runtests.py -v -n unit.states.test_hanamod
