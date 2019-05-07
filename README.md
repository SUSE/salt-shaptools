[![Build Status](https://travis-ci.org/SUSE/salt-shaptools.svg?branch=master)](https://travis-ci.org/SUSE/salt-shaptools)
[![Test Coverage](https://api.codeclimate.com/v1/badges/770395dbb4bb868502b3/test_coverage)](https://codeclimate.com/github/SUSE/salt-shaptools/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/770395dbb4bb868502b3/maintainability)](https://codeclimate.com/github/SUSE/salt-shaptools/maintainability)

# SAP Applications and SUSE Linux Enterprise High Availability salt modules and States

This project has been created to provide salt  modules and states for SAP HANA and other SAP applications and the SLE-HA clustering tools. For that,
it wraps the [shaptools](https://github.com/SUSE/shaptools) project code. The
main idea is to use this module in salt formulas to deploye the these applications easily.

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
sudo salt-call --local --retcode-passthrough -l debug -m . state.template demo/primary.sls
```

### Run in minions
To run the module funcionalities in the minions:

1. Copy the content of **modules** in your "salt://_modules/" (by default /srv/salt/_modules)
2. Copy the content of **states** in your "salt://_states/" (by default /srv/salt/_states)
3. Synchronize modules with the minions. For that run:
```bash
sudo salt '*' saltutil.sync_states
```
4. Execute the module functionalities. For that run:
```bash
sudo salt-call hana.is_installed
```

## How to run the tests
Salt has a quite particular way to execute the tests. As a summary, tests are splitted
in *integration* and *unit* tests. The first group tests the module using actual
salt master/minions, so the setup is more complicated. The *unit* tests in the other
hand only check the code functions.

In order to execute the tests, the test files must be stored in the *salt* project
tests folder sub-folder (integration or unit, for example). By now, as the project
is in a separated repository, the easiest way is to copy our project code to a
actual salt repository and run the tests. For that follow the next instructions:

1. Download the salt project in the same folder of this project:
```bash
git clone git@github.com:saltstack/salt.git
```
2. Create a virtual environment (python2 must be used here) and install dependencies:
```bash
virtualenv saltvirtenv
source saltvirtenv/bin/activate
pip install pyzmq PyYAML pycrypto msgpack-python jinja2 psutil futures tornado pytest-salt mock
pip install -e salt
pip install -e shaptools #put the correct path
```

3. Run the tests. For that:
```bash
cd salt-shaptools
sudo chmod 755 tests/run.sh
./tests/run.sh
```

## Dependencies

List of dependencies are specified in the ["Requirements file"](requirements.txt). Items can be installed using pip:

    pip install -r requirements.txt

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Author

Xabier Arbulu Insausti (xarbulu@suse.com)

## Reviewers

*Pull request* preferred reviewers for this project:
- Xabier Arbulu Insausti (xarbulu@suse.com)
