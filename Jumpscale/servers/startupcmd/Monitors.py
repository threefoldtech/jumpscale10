from Jumpscale import j
import os
import socket


class Monitors:
    @staticmethod
    def tcp_check(cmd):
        """
        :return: nrok,[errormsg]
        """
        res = []
        ok = 0
        for port in cmd.monitor.ports:
            if j.sal.nettools.tcpPortConnectionTest(cmd.runtime.ipaddr, port=port) == False:
                res.append("could not tcp reach %s:%s [tcp_check]" % (ipaddr, port))
            else:
                ok += 1

        return ok, res

    @staticmethod
    def socket_check(cmd):
        """
        :return: nrok,[errormsg]
        """
        if not cmd._local:
            return []

        res = []
        if cmd._local:
            for socketpath in cmd.monitor.socketpaths:
                if not os.path.exists(socketpath):
                    res.append("socket %s does not exist [socket_check]" % (socketpath))
            client = socket.socket(socket.AF_UNIX)
            try:
                client.connect(socketpath)
                ok += 1
            except Exception as e:
                j.shell()
                res.append("could not connect to socket %s [socket_check]" % (socketpath))

        return ok, res

    @staticmethod
    def nrprocess_check(cmd):
        """
        :return: nrok,[errormsg]
        """
        if not cmd._local:
            return 0, []

        if cmd.monitors.maxnrprocesses == 0 and cmd.monitors.minnrprocesses == 0:
            return 0, []

        ps = cmd._get_processes_by_port_or_filter()
        l = len(ps)
        if cmd.monitors.maxnrprocesses > 0:
            if l > cmd.monitors.maxnrprocesses:
                return [
                    "found too many processes, max was:'%s' found '%s' [nrprocess_check]"
                    % (cmd.monitors.maxnrprocesses, l)
                ]
        if cmd.monitors.minnrprocesses > 0:
            if l < cmd.monitors.minnrprocesses:
                return [
                    "found too few processes, min was:'%s' found '%s' [nrprocess_check]"
                    % (cmd.monitors.minnrprocesses, l)
                ]

        return 1, []

    @staticmethod
    def process_check(cmd):
        """
        :return: nrok,[errormsg]
        """
        if not cmd._local:
            return 0, []

        p = cmd.process
        if not p:
            return 1, ["did not find a running process [process_check]"]

        return 1, []