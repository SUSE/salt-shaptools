'''
State module to provide CRMSH (HA cluster) functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       crmsh
:platform:      all

:configuration: This module requires the crm python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    #TODO: create some default configuration parameters if needed

:usage:

.. code-block:: yaml
    cluster-init:
      crm.initialized:
        - name: 'hacluster'
        - watchdog: '/dev/watchdog'
        - interface: 'wlan0'
        - unicast: False
        - admin_ip: '192.168.1.50'
        - sbd: False
'''


# Import python libs
from __future__ import absolute_import, unicode_literals, print_function


# Import salt libs
from salt import exceptions
from salt.ext import six


__virtualname__ = 'crm'


def __virtual__():  # pragma: no cover
    '''
    Only load if the hana module is in __salt__
    '''
    return 'crm.cluster_init' in __salt__


def cluster_absent(
        name='localhost',
        quiet=None):
    """
    Machine is not running as a cluster node

    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Cluster is already not running'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Cluster node {} would be removed'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_remove'](
            host=name,
            force=True,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error removing cluster node'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Cluster node removed'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_initialized(
        name,
        watchdog=None,
        interface=None,
        unicast=None,
        admin_ip=None,
        sbd=None,
        sbd_dev=None,
        quiet=None):
    """
    Machine is running a cluster node

    name
        Cluster name
    watchdog
        Watchdog to set. If None the watchdog is not set
    interface
        Network interface to bind the cluster. If None wlan0 is used
    unicast
        Set the cluster in unicast mode. If None multicast is used
    admin_ip
        Virtual IP address. If None the virtual address is not set
    sbd
        Enable sbd usage. If None sbd is not set
    sbd_dev
        sbd device path. To be used "sbd" parameter must be used too. If None,
            the sbd is set as diskless.
    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Cluster is already initialized'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be initialized'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_init'](
            name=name,
            watchdog=watchdog,
            interface=interface,
            unicast=unicast,
            admin_ip=admin_ip,
            sbd=sbd,
            sbd_dev=sbd_dev,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error initialazing cluster'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Cluster initialized'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_joined(
        name,
        watchdog=None,
        interface=None,
        quiet=None):
    """
    Machine is joined to a cluster as a node

    name
        hostname or ip address of a cluster node to join
    watchdog
        Watchdog to set. If None the watchdog is not set
    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Node is already joined to a cluster'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Node would be joined to {}'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_join'](
            host=name,
            watchdog=watchdog,
            interface=interface,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error joining to the cluster'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Node joined to the cluster'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_configured(
        name,
        url,
        is_xml=None):
    """
    Machine is congifured with the provided configuration file

    name
        Used method. replace, update or push
    url
        Configuration file path or url
    is_xml:
        True if the configuration file is xml type, False otherwise
    """
    method = name

    ret = {'name': method,
           'changes': {},
           'result': False,
           'comment': ''}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Cluster would be configured with method {} and file {}'.format(
            method, url)
        ret['changes']['method'] = method
        ret['changes']['url'] = url
        return ret

    try:
        #  Here starts the actual process
        if __salt__['crm.status']():
            ret['result'] = False
            ret['comment'] = 'Cluster is not created yet. Run cluster_initialized before'
            return ret

        result = __salt__['crm.configure_load'](
            method=method,
            url=url,
            is_xml=is_xml)

        if result:
            ret['comment'] = 'Error configuring the cluster with method {} and file {}'.format(
                method, url)
            ret['result'] = False
            return ret

        ret['changes']['method'] = method
        ret['changes']['url'] = url
        ret['comment'] = 'Cluster properly configured'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret
