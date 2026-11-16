# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The machinery shared by the ssh-family commands.

The resolution of the connection parameters of an inventory host and
the splitting of ssh-style argument lists are shared by the
'debops ssh', 'debops scp' and 'debops sftp' subcommands; the
known_hosts store lives in the sibling :mod:`debops.core.ssh.store`
module, the command-specific builders in the other siblings.
"""

import configparser
import json
import logging
import os
import shlex
import subprocess

from .dns import is_ip_address

logger = logging.getLogger(__name__)

# The ssh options which take a separate value argument, per the usage
# line of the OpenSSH 9.2 ssh(1). Used to walk argument lists where
# ssh options and operands mix. A newer OpenSSH which adds value
# options needs the set revisited; the walk cannot infer the values
# of the options it does not know.
SSH_OPTIONS_WITH_VALUE = set('BbcDEeFIiJLlmOopQRSWw')

# The scp options which take a separate value argument, per the usage
# line of the OpenSSH 9.2 scp(1). The scp grammar differs from the
# ssh one: '-P' is the port and '-B', '-O', '-R' are flags.
SCP_OPTIONS_WITH_VALUE = set('cDFiJlPSX')

# The sftp options which take a separate value argument, per the
# usage line of the OpenSSH 9.2 sftp(1).
SFTP_OPTIONS_WITH_VALUE = set('BbcDFiJlPRsSX')

# The ssh options whose value is optional: they consume the next
# token when one follows, and stand alone at the end of the argument
# list ('ssh -Q' lists the query types).
SSH_OPTIONS_WITH_OPTIONAL_VALUE = {'Q'}

# The ssh flags which the transfer commands accept themselves, passed
# through when they appear in the resolved ssh arguments; the other
# flags are dropped.
SSH_FLAGS_PASSTHROUGH = set('C46')


def value_options_of(parser, passthrough=()):
    """Return the options of a parser which take a value.

    The getopt-style walk needs to know which options carry a value so
    that the token after such an option is not mistaken for an operand.
    The parser's own registered actions are inspected: actions that
    take no value (flags, counters, help) are skipped, everything else
    contributes its short option letters and long option names. The
    'passthrough' letters are the options of the underlying command,
    which the parser does not register but the walk must still honor.

    Returns '(shorts, longs)': the set of the short option letters and
    the list of the long option names which take a value.
    """
    shorts = set(passthrough)
    longs = []
    # The '_actions' attribute is private argparse API; there is no
    # public per-parser action list to inspect instead
    for action in parser._actions:
        if action.nargs == 0:
            continue
        for option_string in action.option_strings:
            if option_string.startswith('--'):
                longs.append(option_string)
            else:
                shorts.add(option_string.lstrip('-'))
    return shorts, longs


def _option_consumes_next(token, value_options, long_value_options):
    """Whether the option token consumes the following token as its
    value.

    A long option with the value attached ('--option=value') does
    not; a short option consumes the next token when its last letter
    takes a value and the token carries no attached value ('-o value',
    '-qL value'), while the attached form ('-oValue') does not.
    """
    if token.startswith('--'):
        if '=' in token:
            return False
        return token in long_value_options
    if len(token) == 2:
        return token[1] in value_options
    # A cluster of short options; the first letter which takes a
    # value ends the option part of the token
    for position, letter in enumerate(token[1:]):
        if letter in value_options:
            return position + 2 == len(token)
    return False


def split_options_operands(tokens, value_options, long_value_options=(),
                           stop_at_operand=True):
    """Split an argument list into the options and the operands.

    The walk follows the getopt permutation: an option which takes a
    value keeps the next token as its value, and the tokens which are
    neither options nor option values are the operands, in the order
    they appear. With 'stop_at_operand' the walk ends at the first
    operand and the tokens after it are returned as the 'tail', in
    their places -- the arguments which follow the operand on the
    command line, such as the remote command of ssh, must not be
    permuted. Without it the walk covers the whole list, the way the
    multi-operand commands permute.

    The 'value_options' are the option letters which take a value and
    'long_value_options' the long option names; the set carries the
    options of the parser and the ones passed through to the command.
    The '--' marker ends the options; the next token is an operand
    even when it looks like an option.

    An option which requires a value and finds none raises ValueError;
    left valueless, the command would consume an operand as the value
    instead. The options with an optional value stand alone.
    """
    options = []
    operands = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == '--':
            index += 1
            # The tokens after the marker are the operands, even when
            # they look like options
            if stop_at_operand:
                if index < len(tokens):
                    operands.append(tokens[index])
                    index += 1
            else:
                operands.extend(tokens[index:])
                index = len(tokens)
            break
        if not token.startswith('-') or token == '-':
            operands.append(token)
            index += 1
            if stop_at_operand:
                break
            continue
        options.append(token)
        if _option_consumes_next(token, value_options,
                                 long_value_options):
            if index + 1 < len(tokens):
                index += 1
                options.append(tokens[index])
            elif token[-1] not in SSH_OPTIONS_WITH_OPTIONAL_VALUE:
                raise ValueError('the option ' + token
                                 + ' requires a value')
        index += 1
    tail = tokens[index:] if stop_at_operand else []
    return options, operands, tail


def split_host_path(operand):
    """Split an scp/sftp operand into the host part and the path.

    The operand grammar: '[[user@]host:]path'; the colon which
    separates the host from the path is the first colon, or the first
    colon after the closing bracket of a bracketed address. Returns
    '(None, operand)' when the operand carries no colon.
    """
    bracket_end = operand.find(']')
    if bracket_end != -1:
        candidate = operand.find(':', bracket_end)
    else:
        candidate = operand.find(':')
    if candidate == -1:
        return None, operand
    return operand[:candidate], operand[candidate + 1:]


def split_operand(operand):
    """Split an scp operand into the user, the host and the path.

    The scp operand grammar: '[[user@]host:]path'; the host part may
    carry a 'user@' prefix and a bracketed IPv6 address. Returns
    '(None, None, operand)' when the operand is a local path.
    """
    host_part, path = split_host_path(operand)
    if host_part is None:
        return None, None, operand
    user = None
    if '@' in host_part:
        # ssh splits the user at the last '@' of the destination, the
        # way 'ssh -G a@b@c' reports the user 'a@b'
        user, _, host_part = host_part.rpartition('@')
    host = host_part.strip('[]')
    return user, host, path


def compose_options(pairs):
    """Return the argv list for ssh option pairs, without duplicates.

    The items are '(option, value)' tuples and bare flag tokens. The
    first occurrence of an item wins, matching the way ssh treats its
    configuration; the result is the flat argv list the options
    compose into.
    """
    argv = []
    for item in dict.fromkeys(pairs):
        if isinstance(item, str):
            argv.append(item)
        else:
            argv.extend(item)
    return argv


def bracket_ipv6(host):
    """Return the host in the form the scp and sftp grammars parse as
    one address.

    An IPv6 literal carries colons, which the transfer grammars read
    as the host/path separator; the bracketed form survives them.
    """
    if is_ip_address(host) and ':' in host:
        return '[' + host + ']'
    return host


def transfer_executable(project, command):
    """Return the transfer binary which the configuration names.

    The 'scp_executable' and 'sftp_executable' options of the view's
    'ansible.cfg' and their environment variables select the binary;
    the inventory variables need a host, which the handoff invocation
    does not resolve.
    """
    try:
        return (os.environ.get('ANSIBLE_' + command.upper()
                               + '_EXECUTABLE')
                or project.ansible_cfg.get_option(
                    command + '_executable', section='ssh_connection'))
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None


def without_known_hosts_options(tokens):
    """Drop the 'UserKnownHostsFile' options from the resolved ssh
    arguments.

    The options appear as an '-o' option with its value, as the
    attached '-oUserKnownHostsFile=...' form, or as the bare value
    token -- with the equals sign of the option form or the space of
    the configuration form; the rest of the arguments keep their
    order.
    """
    kept = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.startswith('-oUserKnownHostsFile'):
            index += 1
            continue
        if token == '-o' and index + 1 < len(tokens) \
                and tokens[index + 1].startswith('UserKnownHostsFile'):
            index += 2
            continue
        if token.startswith('UserKnownHostsFile'):
            index += 1
            continue
        kept.append(token)
        index += 1
    return kept


def translate_ssh_args(ssh_args):
    """Translate ssh arguments into the '-o' option pairs which the
    file-transfer commands accept for their ssh connections.

    '-J destination' becomes the ('-o', 'ProxyJump=destination') pair,
    '-o value' pairs pass through unchanged, the flags the transfer
    commands accept themselves ('-C', '-4', '-6') pass through as bare
    tokens, and the options which configure port and packet forwards
    -- meaningless for a file transfer -- are dropped and reported.
    Returns the list of '(option, value)' pairs and bare tokens to add
    to the command, and the list of the dropped arguments as display
    strings.
    """
    tokens = (shlex.split(ssh_args)
              if isinstance(ssh_args, str) else list(ssh_args))
    translated = []
    dropped = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        letter = token[1] if len(token) > 1 else ''
        attached = len(token) > 2

        if token == '-J' or (letter == 'J' and attached):
            value = token[2:] if attached else (
                tokens[index + 1] if index + 1 < len(tokens) else None)
            if value is None:
                dropped.append(token)
                index += 1
                continue
            translated.append(('-o', 'ProxyJump=' + value))
            index += 1 if attached else 2
        elif token == '-o' or (letter == 'o' and attached):
            if attached:
                translated.append(('-o', token[2:]))
                index += 1
            elif index + 1 < len(tokens):
                translated.append(('-o', tokens[index + 1]))
                index += 2
            else:
                dropped.append(token)
                index += 1
        elif len(token) == 2 and token[1] in SSH_FLAGS_PASSTHROUGH:
            # The compression and address-family flags of ssh are
            # flags of the transfer commands as well
            translated.append(token)
            index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE and attached:
            dropped.append(token)
            index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE:
            if index + 1 < len(tokens):
                dropped.append(token + ' ' + tokens[index + 1])
                index += 2
            else:
                # A value option without its value is meaningless for
                # a transfer; it is dropped like the other leftovers
                dropped.append(token)
                index += 1
        else:
            dropped.append(token)
            index += 1
    return translated, dropped


def _split_hop(hop):
    """Split a jump hop specification into the destination of the jump
    process and its port.

    The grammar of a '-J' hop: '[user@]host[:port]', with brackets
    around an IPv6 address which carries a port. The plain destination
    grammar of ssh does not parse 'host:port', so the port is carried
    as the '-p' option of the jump process, the way the implicit
    ProxyCommand of ssh carries it.
    """
    user = None
    hostport = hop
    if '@' in hostport:
        user, _, hostport = hostport.rpartition('@')
    port = None
    if hostport.startswith('[') and ']' in hostport:
        host, _, remainder = hostport[1:].partition(']')
        host = '[' + host + ']'
        if remainder.startswith(':') and remainder[1:].isdigit():
            port = remainder[1:]
    else:
        host, separator, candidate = hostport.rpartition(':')
        if not separator or not candidate.isdigit():
            host = hostport
        else:
            port = candidate
    destination = (user + '@' if user else '') + host
    return destination, port


def proxy_jump_command(hop, option_pairs):
    """Return the ProxyCommand option value which runs the connection
    through a jump host with the given option pairs of the parent.

    OpenSSH builds the connection to a jump host from the parent
    command line as a child 'ssh -W [%h]:%p <hop>' which inherits only
    the '-F' and '-v' options of the parent: the options DebOps
    composes for the destination -- the known_hosts store, the host
    key checking mode, the connection timeout -- never reach the jump
    process. The explicit ProxyCommand carries them.

    The value is executed by the shell, so every element which may
    carry shell syntax is quoted: the '-W [%h]:%p' forwarding tokens
    are quoted the way the implicit ProxyJump command of ssh quotes
    them, and the destination of the jump process is quoted with the
    shell quoting rules. The option pairs arrive already in their
    final form; the store path inside them is quoted by
    'quote_store_path'.
    """
    destination, port = _split_hop(hop)
    parts = ['ssh']
    if port:
        parts.extend(['-p', port])
    for pair in option_pairs:
        if isinstance(pair, tuple):
            parts.extend(pair)
        else:
            parts.append(pair)
    parts.extend(['-W', shlex.quote('[%h]:%p')])
    parts.append(shlex.quote(destination))
    return 'ProxyCommand=' + ' '.join(parts)


class JumpRewriter:
    """Rewrite the structured jump options of a composed ssh command
    into explicit ProxyCommand options.

    The '-J hop', '-Jhop', '-o ProxyJump=hop' and '-oProxyJump=hop'
    forms of a single hop become '-o ProxyCommand=...' options which
    run the jump connection with the option pairs given at the
    construction -- the trust and mode options of the parent command.
    The rewriting instance accumulates its state across the argument
    groups of one command, so a 'ProxyCommand' of the operator in one
    group and a structured jump in another are recognized as the
    ambiguity they are: 'check' raises ValueError when both appear,
    because the ProxyCommand would shadow the jump handling of DebOps
    and the discovered jump would not be the bastion the connection
    actually traverses.

    A comma-separated hop list, a jump chain, is left unchanged: every
    additional hop would need another nested ProxyCommand layer with
    its own quoting; the chains are a documented limitation of the
    suite.
    """

    def __init__(self, option_pairs):
        self.option_pairs = list(option_pairs)
        self._jump_rewritten = False
        self._proxy_seen = False

    def rewrite_tokens(self, tokens):
        """Return the token list with the structured jumps rewritten.

        The '-o' options are consumed together with their value token,
        so a value which resembles a jump option is never inspected on
        its own.
        """
        result = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == '-o':
                value = tokens[index + 1] if index + 1 < len(tokens) else None
                if value is not None and value.startswith('ProxyJump='):
                    hop = value[len('ProxyJump='):]
                    if hop and ',' not in hop:
                        self._jump_rewritten = True
                        result.append('-o')
                        result.append(
                            proxy_jump_command(hop, self.option_pairs))
                        index += 2
                        continue
                if value is not None and value.startswith('ProxyCommand='):
                    self._proxy_seen = True
                result.append(token)
                if value is not None:
                    result.append(value)
                    index += 2
                else:
                    index += 1
                continue
            letter = token[1] if len(token) > 1 else ''
            attached = len(token) > 2
            hop = None
            consumed = 1
            if token == '-J' or (letter == 'J' and attached):
                hop = token[2:] if attached else (
                    tokens[index + 1] if index + 1 < len(tokens) else None)
                consumed = 2 if (not attached and hop is not None) else 1
            elif attached and letter == 'o' \
                    and token[2:].startswith('ProxyJump='):
                hop = token[2:][len('ProxyJump='):]
            elif token.startswith('ProxyCommand='):
                self._proxy_seen = True
            if hop is None:
                result.append(token)
                index += consumed
                continue
            if not hop or ',' in hop:
                result.extend(tokens[index:index + consumed])
                index += consumed
                continue
            self._jump_rewritten = True
            result.extend(['-o', proxy_jump_command(hop, self.option_pairs)])
            index += consumed
        return result

    def rewrite_pairs(self, pairs):
        """Return the option pair list with the structured jumps
        rewritten."""
        result = []
        for pair in pairs:
            if isinstance(pair, tuple) and pair[0] == '-o' \
                    and pair[1].startswith('ProxyJump='):
                hop = pair[1][len('ProxyJump='):]
                if hop and ',' not in hop:
                    self._jump_rewritten = True
                    result.append(
                        ('-o', proxy_jump_command(hop, self.option_pairs)))
                    continue
            if isinstance(pair, tuple) and pair[0] == '-o' \
                    and pair[1].startswith('ProxyCommand='):
                self._proxy_seen = True
            elif isinstance(pair, str) and pair.startswith('ProxyCommand='):
                self._proxy_seen = True
            result.append(pair)
        return result

    def check(self):
        """Raise ValueError when a ProxyCommand coexists with a
        structured jump of the same command."""
        if self._jump_rewritten and self._proxy_seen:
            raise ValueError(
                'The connection defines both a ProxyCommand and a jump '
                'host; the ProxyCommand would shadow the jump handling '
                'of DebOps, so the connection is refused')


# The connection options of the ssh connection plugin, each in the
# resolution order the plugin applies: the inventory variables over
# the environment over the option of the 'ansible.cfg'. The table
# carries the variable names, the environment variable and the
# configuration option of each connection parameter; the 'debops ssh'
# commands resolve them the same way the plugin does, so a connection
# composed by DebOps reaches the host the same way an Ansible
# connection does.
CONNECTION_OPTIONS = (
    # (key, variable names, environment name, ini section, ini key)
    ('destination', ('ansible_host', 'ansible_ssh_host'),
     None, None, None),
    ('user', ('ansible_user', 'ansible_ssh_user'),
     'ANSIBLE_REMOTE_USER', 'defaults', 'remote_user'),
    ('port', ('ansible_port', 'ansible_ssh_port'),
     'ANSIBLE_REMOTE_PORT', 'defaults', 'remote_port'),
    ('identity', ('ansible_private_key_file',
                  'ansible_ssh_private_key_file'),
     'ANSIBLE_PRIVATE_KEY_FILE', 'defaults', 'private_key_file'),
    ('ssh_args', ('ansible_ssh_args',),
     'ANSIBLE_SSH_ARGS', 'ssh_connection', 'ssh_args'),
    ('common_args', ('ansible_ssh_common_args',),
     'ANSIBLE_SSH_COMMON_ARGS', 'ssh_connection', 'ssh_common_args'),
    ('extra_args', ('ansible_ssh_extra_args',),
     'ANSIBLE_SSH_EXTRA_ARGS', 'ssh_connection', 'ssh_extra_args'),
    ('ssh_executable', ('ansible_ssh_executable',),
     'ANSIBLE_SSH_EXECUTABLE', 'ssh_connection', 'ssh_executable'),
    ('scp_executable', ('ansible_scp_executable',),
     'ANSIBLE_SCP_EXECUTABLE', 'ssh_connection', 'scp_executable'),
    ('scp_extra_args', ('ansible_scp_extra_args',),
     'ANSIBLE_SCP_EXTRA_ARGS', 'ssh_connection', 'scp_extra_args'),
    ('sftp_executable', ('ansible_sftp_executable',),
     'ANSIBLE_SFTP_EXECUTABLE', 'ssh_connection', 'sftp_executable'),
    ('sftp_extra_args', ('ansible_sftp_extra_args',),
     'ANSIBLE_SFTP_EXTRA_ARGS', 'ssh_connection', 'sftp_extra_args'),
    ('timeout', (), 'ANSIBLE_TIMEOUT', 'defaults', 'timeout'),
)


def resolve_host(project, host):
    """Return the connection parameters of an inventory host.

    The parameters come from the Ansible inventory, resolved with
    'ansible-inventory --host' the same way the Ansible runners resolve
    it, and follow the option resolution of the ssh connection plugin
    (:data:`CONNECTION_OPTIONS`): the inventory variables over the
    environment over the options of the 'ansible.cfg'. Returns a dict
    with the keys of :data:`CONNECTION_OPTIONS`; parameters which
    nothing defines are None.

    Raises ValueError when the host is not defined in the inventory of
    the project's view, ChildProcessError when the resolution cannot
    run.
    """
    binary = project.config.raw['binaries']['ansible-inventory']
    try:
        process = subprocess.run(
            [binary, '--host', host], cwd=project.path,
            env=project.environment(), capture_output=True, text=True)
    except OSError as error:
        raise ChildProcessError(
            'Cannot run the inventory resolution: ' + str(error))
    if process.returncode != 0:
        detail = (process.stderr.strip().splitlines() or [''])[-1]
        raise ValueError('Cannot resolve the host "' + host + '": '
                         + detail)
    try:
        variables = json.loads(process.stdout)
    except ValueError:
        raise ValueError('Cannot resolve the host "' + host + '": the '
                         'inventory returned no usable host variables')

    parameters = {}
    for key, var_names, env_name, section, ini_key in CONNECTION_OPTIONS:
        value = next((variables[name] for name in var_names
                      if variables.get(name)), None)
        if not value and env_name:
            value = os.environ.get(env_name)
        if not value and ini_key:
            try:
                value = project.ansible_cfg.get_option(ini_key,
                                                       section=section)
            except (configparser.NoOptionError,
                    configparser.NoSectionError):
                value = None
        parameters[key] = value
    destination = parameters['destination'] or host
    if destination.startswith('-'):
        raise ValueError(
            'The ansible_host of the host "' + host + '" looks like an '
            'SSH option instead of a host name or address: ' + destination)
    parameters['destination'] = destination
    user = parameters['user']
    if user is not None and user.startswith('-'):
        # Composed into the destination tokens of the transfers, such
        # a value would be parsed as an ssh option by sftp
        raise ValueError(
            'The user of the host "' + host + '" looks like an SSH '
            'option instead of an account name: ' + user)
    for key in ('port', 'timeout'):
        value = parameters[key]
        if value is not None and not isinstance(value, (str, int)):
            # A list or a mapping would compose into garbage argv
            raise ValueError(
                'The "' + key + '" of the host "' + host + '" is not '
                'a usable value: ' + repr(value))
    for key, value in parameters.items():
        if isinstance(value, str) and ('{{' in value or '{%' in value):
            # The '--host' dump of 'ansible-inventory' does not render
            # the templates of the inventory variables; a value which
            # still carries the delimiters would reach the command
            # line literally
            raise ValueError(
                'The "' + key + '" connection parameter of the host "'
                + host + '" carries an unrendered Ansible template ('
                + value + '); the ssh suite does not render the '
                'inventory templates -- define the value literally')
    return parameters


def resolve_patterns(project, patterns):
    """Expand Ansible inventory patterns into inventory host names.

    The patterns are expanded by the 'ansible' binary with
    '--list-hosts', the same pattern engine the runners use, so
    'all', the group names, the wildcards and the unions work. The
    parsed output is the human-oriented listing of the 'ansible' tool
    and not a versioned interface -- a format change of ansible-core
    surfaces here, and the raw output is logged at the debug level for
    such a case. Returns '(hosts, unmatched)': the deduplicated host
    names in the order of the patterns, and the patterns which matched
    no host. Raises ValueError when the expansion fails,
    ChildProcessError when it cannot run.
    """
    binary = project.config.raw['binaries']['ansible']
    hosts = []
    unmatched = []
    for pattern in patterns:
        try:
            process = subprocess.run(
                [binary, pattern, '--list-hosts'], cwd=project.path,
                env=project.environment(), capture_output=True, text=True)
        except OSError as error:
            raise ChildProcessError(
                'Cannot run the pattern expansion: ' + str(error))
        if process.returncode != 0:
            detail = (process.stderr.strip().splitlines() or [''])[-1]
            raise ValueError('Cannot expand the pattern "' + pattern
                             + '": ' + detail)
        logger.debug('The pattern expansion of "' + pattern + '" wrote: '
                     + process.stdout.strip().replace('\n', ' | '))
        matched = []
        in_list = False
        for line in process.stdout.splitlines():
            if line.startswith('['):
                continue
            if not in_list:
                if line.lstrip().startswith('hosts ('):
                    in_list = True
                continue
            if not line.strip():
                continue
            if line.startswith((' ', '\t')):
                matched.append(line.strip())
            else:
                break
        for host in matched:
            if host not in hosts:
                hosts.append(host)
        if not matched:
            unmatched.append(pattern)
    return hosts, unmatched


def resolve_destination(project, name):
    """Resolve the destination of a single-host ssh suite command.

    The destination must be a literal inventory host name: the name is
    expanded the way the Ansible patterns are, and only a name which
    matches itself resolves -- 'all' and the other patterns are the
    domain of 'debops ssh rescan', even when they would match a single
    host. Raises ValueError when the name is not defined in the
    inventory or when it matches several hosts, ChildProcessError when
    the expansion cannot run.
    """
    hosts, _ = resolve_patterns(project, [name])
    if not hosts:
        raise ValueError('Cannot resolve the host "' + name + '": it is '
                         'not defined in the inventory of the view')
    if hosts == [name]:
        return resolve_host(project, name)
    if len(hosts) == 1:
        raise ValueError('The destination "' + name + '" is an '
                         'inventory pattern; a single host destination '
                         'is required')
    raise ValueError('The destination "' + name + '" matches '
                     + str(len(hosts)) + ' inventory hosts; a single '
                     'host destination is required')


def ssh_executable(project):
    """Return the ssh binary which the connections use.

    The 'ssh_executable' option of the view's 'ansible.cfg' overrides
    the configured default.
    """
    try:
        return project.ansible_cfg.get_option(
            'ssh_executable', section='ssh_connection')
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None
