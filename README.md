[![Package CI](https://github.com/SUSE/salt-shaptools/actions/workflows/salt-shaptools-ci.yml/badge.svg)](https://github.com/SUSE/salt-shaptools/actions/workflows/salt-shaptools-ci.yml)
[![Test Coverage](https://api.codeclimate.com/v1/badges/770395dbb4bb868502b3/test_coverage)](https://codeclimate.com/github/SUSE/salt-shaptools/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/770395dbb4bb868502b3/maintainability)](https://codeclimate.com/github/SUSE/salt-shaptools/maintainability)

# SAP Applications and SUSE Linux Enterprise High Availability salt modules and States

This project has been created to provide salt modules and states for SAP HANA and other SAP applications and the SLE-HA clustering tools. For that,
it wraps the [shaptools](https://github.com/SUSE/shaptools) project code. The
main idea is to use this module in salt formulas to deploy these applications easily.

## Installation and usage

**INFO:** Currently this project has been created as an independent project, but
the idea is to merge to the [salt](https://github.com/saltstack/salt) project
to extend it with these new functionalities.

### Run locally

To run the module functionalities locally run:

```bash
cd salt-shaptools
sudo salt-call --local -m modules hana.is_installed
```

To run the state modules (there is a demo example in the demo folder) run:

```bash
cd salt-shaptools
sudo salt-call --retcode-passthrough -l debug -m . state.template demo/primary.sls
```

### Run in minions

To run the module funcionalities in the minions:

1. Copy the content of **modules** in your "salt://\_modules/" (by default /srv/salt/\_modules)
2. Copy the content of **states** in your "salt://\_states/" (by default /srv/salt/\_states)
3. Synchronize modules with the minions. For that run:

```bash
sudo salt-call  saltutil.sync_all
```

4. Execute the module functionalities. For that run:

```bash
sudo salt-call hana.is_installed
```

## Writing unit test

You can have look at: https://docs.saltstack.com/en/latest/topics/development/tests/unit.html

## How to run the tests

Salt has a quite particular way to execute the tests. As a summary, tests are splitted
in _integration_ and _unit_ tests. The first group tests the module using actual
salt master/minions, so the setup is more complicated. The _unit_ tests in the other
hand only check the code functions.

In order to execute the tests, the test files must be stored in the _salt_ project
tests folder sub-folder (integration or unit, for example). By now, as the project
is in a separated repository, the easiest way is to copy our project code to a
actual salt repository and run the tests. For that follow the next instructions:

1. Download 2 **needed extra projects**: (saltstack and shaptools)

```bash
git clone --depth=50 https://github.com/openSUSE/salt
git clone https://github.com/SUSE/shaptools.git
```

Your directory layout should looks like ( all the 3 dirs are in same three dir level)

```
- salt-shaptools
- salt
- shaptools
```

2. Create a virtual environment, inside the `salt-shaptools` dir and install dependencies:

```bash
virtualenv saltvirtenv
source saltvirtenv/bin/activate
pip install pyzmq PyYAML pycrypto msgpack-python jinja2 psutil futures tornado pytest-salt mock pytest-cov
pip install -e ../salt
pip install -e ../shaptools
rm ../salt/tests/conftest.py # remove this file from the saltstack repo
```

3. Run the tests. For that:

```bash
cd salt-shaptools
sudo chmod 755 tests/run.sh
./tests/run.sh
```

4. Running your modules/states:

For testing/running modules:

```
salt-call --local saptune.apply_solution "SAP-ASE"

```

For testing/running states:

```
salt-call --local state.single saptune.solution_applied "HANA"
```

## Dependencies

List of dependencies are specified in the ["Requirements file"](requirements.txt). Items can be installed using pip:

    pip install -r requirements.txt

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Author

Xabier Arbulu Insausti (xarbulu@suse.com)

## Reviewers

_Pull request_ preferred reviewers for this project:

- Xabier Arbulu Insausti (xarbulu@suse.com)
