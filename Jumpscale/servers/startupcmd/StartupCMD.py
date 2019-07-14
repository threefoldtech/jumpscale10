from Jumpscale import j

import time


class StartupCMD(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.startupcmd.1
        name* = ""
        cmd_start = ""
        interpreter = "bash,jumpscale,direct,python" (E)  #direct means we will not put in bash script
        cmd_stop = ""
        debug = False (b)
        path = ""
        env = (dict)
        ports = (LI)
        ports_udp = (LI)
        timeout = 10
        process_strings = (ls)
        process_strings_regex = (ls)
        pid = 0
        executor = "tmux,corex,foreground,background" (E)
        daemon = true (b)
        hardkill = false (b)

        state = "init,running,error,stopped,stopping,down,notfound" (E)
        corex_client_name = "default" (S)
        corex_id = (S)
        
        error = "" (S)
        
        time_start = (T)
        time_refresh = (T)
        time_stop = (T)

        """

    def _init(self, **kwargs):
        self._pane_ = None
        self._corex_local_ = None
        self._logger_enable()

        if self.executor == "corex":
            self._corex_clean()
        self.refresh()

    def _reset(self):
        self.time_start = 0
        self.time_stop = 0
        self.pid = 0
        self.state = "init"
        self.corex_id = ""

    @property
    def _cmd_path(self):
        return j.sal.fs.joinPaths(j.servers.startupcmd._cmdsdir, self.name)

    def _error_raise(self, msg):
        msg = "error in startupcmd :%s\n%s\n" % (self.name, msg)
        raise RuntimeError(msg)

    def delete(self):
        j.application.JSBaseConfigClass.delete(self)
        j.sal.fs.remove(self._cmd_path)
        j.sal.fs.remove(self._cmd_path + ".cmd")
        j.sal.fs.remove(self._cmd_path + ".sh")
        j.sal.fs.remove(self._cmd_path + ".lua")
        j.sal.fs.remove(self._cmd_path + ".py")

    @property
    def process(self):
        if self.executor == "corex" and not self._corex_local:
            return self._error_raise("cannot get process object from remote corex")

        def notify_p(p):
            if p.status().casefold() in ["running", "sleeping", "idle"]:
                self._notify_state("running")
                if p.pid != self.pid:
                    self.pid = p.pid
                    self.save()
            else:
                self._notify_state("down")
            return p

        if self.pid:
            p = j.sal.process.getProcessObject(self.pid, die=False)
            if not p:
                self.pid = 0
            else:
                return notify_p(p)

        if self._local:
            ps = self._get_processes_by_port_or_filter()
            if len(ps) == 1:
                return notify_p(ps[0])

        if not self.pid:
            return

        return j.sal.process.getProcessObject(self.pid)

    def _get_processes_by_port_or_filter(self, process_filter=True, ports=True):
        if self.executor == "corex" and not self._corex_local:
            return self._error_raise("cannot get process object from remote corex")

        pids_done = []
        res = []

        if ports:
            for port in self.ports:
                try:
                    p = j.sal.process.getProcessByPort(port)
                except Exception as e:
                    if str(e).find("it's a zombie") != -1:
                        continue

                if p and p.pid:
                    res.append(p)
                    pids_done.append(p.pid)

        if process_filter:
            for pstring in self.process_strings:
                for pid in j.sal.process.getPidsByFilter(self.process_strings):
                    p = j.sal.process.getProcessObject(pid)
                    if p.pid not in pids_done:
                        pids_done.append(p.pid)
                        res.append(p)

            if self.process_strings_regex != []:
                for pid in j.sal.process.getPidsByFilter(regex_list=self.process_strings_regex):
                    p = j.sal.process.getProcessObject(pid)
                    if p.pid not in pids_done:
                        pids_done.append(p.pid)
                        res.append(p)
        # we return all processes which match
        return res

    def _kill_processes_by_port_or_filter(self):
        """
        will return all processes which match the regex of filter string
        :return:
        """
        for p in self._get_processes_by_port_or_filter():
            p.kill()

    def _softkill(self):
        """

        :return: True if it actually tried a softkill, otherwise False
        """
        if self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_stop(self.corex_id)
            return True
        if self._local:
            if self.cmd_stop:
                cmd = j.tools.jinja2.template_render(text=self.cmd_stop, args=self.data._ddict)
                self._log_warning("stopcmd:%s" % cmd)
                rc, out, err = j.sal.process.execute(cmd, die=False)
                return True
        return False

    def _hardkill(self, signal=9):
        """

        :param signal:
        :return: True if we know hardkill worked, otherwise False
        """

        # will try to use process manager but this only works for local
        if self._local:
            if self.pid and self.pid > 0:
                self._log_info("found process to stop:%s" % self.pid)
                p = self.process
                if p and self.state == "running":
                    p.kill()
                    time.sleep(0.2)

            self._kill_processes_by_port_or_filter()

        if self.executor == "background":
            # only process mechanism above can have worked
            return False
        elif self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_kill(self.corex_id)
            self._notify_state("stopped")
            return True
        elif self.executor == "tmux":
            # TMUX
            self._pane.kill()
            self._pane.window.kill()
            # if [item.name for item in self._pane.window.panes] == ["main"]:
            #     # means we only had the main tmux window left, that one can be closed
            #     self._pane.mgmt.window.server.kill_server()
            self._pane_ = None
            self._notify_state("stopped")
            return True

    def refresh(self):
        self._log_info("refresh: %s" % self.name)

        self.time_refresh = j.data.time.epoch

        if self.executor == "corex":
            self._corex_refresh()
            if self._local:
                # self.is_running()  # will refresh the state automatically
                self.process

        elif self.executor == "tmux" or self.executor == "background":
            # self.is_running()
            self.process
        elif self.executor == "foreground":
            pass
        else:
            raise RuntimeError("not supported")

    def stop(self, force=False, waitstop=True, die=True):
        """

        :param force: will do a hardkill after the softkill even if it measures down
        :param die: will die if we confirmed is still alive
        :param waitstop: will wait to stop
        :return: True (was ok), -1: we don't know, False (it did not stop, only relevant if die=False)
        """
        self._log_warning("stop: %s" % self.name)

        if self.is_running() == False:  # if we don't know it will be -1
            return

        self._notify_state("stopping")

        if self._softkill():
            # means we really tried a softkill
            stopped = self.wait_stopped(die=False, timeout=self.timeout)
            if stopped == True and force == False:  # this means we really know for sure it died
                return True

        self._hardkill()  # will remove tmux pane or other hard method of stopping

        if waitstop:
            self.wait_stopped(die=die, timeout=self.timeout)
            if die:
                return True
        return -1  # we could not know for sure

    def _notify_state(self, state):
        """
        make sure we keep the state table healthy

        state = "init,running,error,stopped,stopping,down,notfound" (E)

        :param state:
        :return:
        """
        if self.state != state:
            if state in ["down", "stopped", "stopping", "notfound", "init"]:
                self.time_stop = j.data.time.epoch
            if state in ["running"]:
                self.time_start = j.data.time.epoch
            self.state = state
            self.save()

    def is_running(self):

        # self._log_debug("running:%s" % self.name)
        if self._local and self.ports != []:
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port) == False:
                    self._notify_state("down")
                    return False
                else:
                    return True

        if self._local and self.ports_udp != []:
            for port in self.ports_udp:
                if j.sal.nettools.udpPortConnectionTest(ipaddr="localhost", port=port) == False:
                    self._notify_state("down")
                    return False
                else:
                    return True

        if self.executor == "corex":
            if not self.pid and not self.corex_id:
                return self._error_raise("cannot check running don't have pid or corex_id")
            self.refresh()
            j.shell()

        if self._local:
            p = self.process
            if p:
                # we found a process so can take decision now
                if self.state == "running":
                    # self process sets the state
                    return True
                else:
                    return False
            else:
                if self.ports != [] or self.process_strings != "" or self.process_strings_regex != "":
                    # we check on ports or process strings so we know for sure its down
                    if len(self._get_processes_by_port_or_filter()) > 0:
                        self._notify_state("running")
                        return True
                    self._notify_state("down")
                    return False

        return -1  # means we don't know

    def wait_stopped(self, die=True, timeout=10):
        """

        :param die:
        :param timeout:
        :return: will return True if it stopped, False if it did not work, -1 if we don't know
                 if die and stopped will raise error
        """
        self._log_debug("wait_stopped:%s (now:%s)" % (self.name, j.data.time.epoch))
        assert timeout > 1
        end = j.data.time.epoch + timeout

        if self._local:
            # are going to wait for first conditions
            if self.ports != [] or self.ports_udp != []:
                while j.data.time.epoch < end:
                    nr = 0
                    nr_port_check = len(self.ports) + len(self.ports_udp)
                    for port in self.ports:
                        if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port) == False:
                            nr += 1
                    for port in self.ports_udp:
                        if j.sal.nettools.udpPortConnectionTest(ipaddr="localhost", port=port) == False:
                            nr += 1
                    if nr == nr_port_check and nr > 0:
                        self._log_info("IS HALTED based on TCP/UDP %s" % self.name)
                        break

                    time.sleep(0.05)

            # if self.process_strings_regex or self.process_strings:
            #     self._log_debug("wait till processes %s dissapear from mem" % self.name)
            #     while self.state != "stopped" and j.data.time.epoch < end:
            #         if len(self._get_processes_by_port_or_filter(ports=False)) == 0:
            #             self.state = "stopped"
            #             self.save()
            #         j.shell()
            #         time.sleep(0.2)

            if not j.data.time.epoch < end:
                # we got timeout on waiting for the stopping
                self._log_warning("stop did not happen in time on:%s" % self)
                if die:
                    # print(j.data.time.epoch)
                    return self._error_raise("could not stop in time, timeout happened")
                return False

            p = self.process
            if p:
                if self.state in ["running"]:
                    if die:
                        return self._error_raise("could not stop")
                    return False
                else:
                    return True
            else:
                return -1

            if die:
                return self._error_raise("could not stop")
            return -1  # we don't know

    def wait_running(self, die=True, timeout=10):
        if timeout is None:
            timeout = self.timeout
        end = j.data.time.epoch + timeout
        if self.ports == [] and self.ports_udp == []:
            time.sleep(0.5)  # need this one or it doesn't check if it failed
        self._log_debug("wait to run:%s (timeout:%s)" % (self.name, timeout))
        while j.data.time.epoch < end:
            if self._local:
                r = self.is_running()
                # self._log_debug("check run: now:%s end:%s" % (j.data.time.epoch, end))
                if r is True:
                    return True
            else:
                r = self._corex_client.process_info_get(pid=self.pid)
                time.sleep(1)
                r = self._corex_client.process_info_get(pid=self.pid)
                if r["state"] in ["stopped", "stopping", "error"]:
                    self.error = self.logs
                    self.state = "error"
                    return False
                elif r["state"] in ["running"]:
                    return True
                else:
                    j.shell()
        if die:
            return self._error_raise("could not start")
        else:
            return False

    def start(self, reset=False, checkrunning=True):
        """

        :param reset:
        :param checkrunning:
        :param foreground: means will not do in e.g. tmux
        :return:
        """
        self._log_debug("start:%s" % self.name)

        if self.executor != "foreground":
            if reset:
                self.stop()
                self._hardkill()

        if self.is_running() == True:
            self._log_info("no need to start was already started:%s" % self.name)
            return

        if not self.cmd_start:
            raise ValueError("please make sure self.cmd_start has been specified")

        if "\n" in self.cmd_start.strip():
            C = self.cmd_start
        elif self.interpreter == "bash":
            C = """            
            reset
            {% if cmdobj.executor=='tmux' %}
            tmux clear
            {% endif %}
            clear
            cat /sandbox/var/cmds/{{name}}.sh
            set +ex
            {% for key,val in args.items() %}
            export {{key}}='{{val}}'
            {% endfor %}
            . /sandbox/env.sh
            {% if cmdpath != None %}
            cd {{cmdpath}}
            {% endif %}
            {{cmd}}

            """
        elif self.interpreter in ["direct", "python"]:
            C = self.cmd_start
        elif self.interpreter == "jumpscale":
            C = """
            from Jumpscale import j
            {% if cmdpath %}
            j.sal.fs.changeDir("{{cmdpath}}")
            {% endif %}
            {{cmd}}
            """

        C2 = j.core.text.strip(C)

        C3 = j.tools.jinja2.template_render(
            text=C2, args=self.env, cmdpath=self.path, cmd=self.cmd_start, name=self.name, cmdobj=self
        )

        self._log_debug("\n%s" % C3)

        if not self._local:
            # when not local we always have to wrap in in such a way we can execute it remotely so without file
            tpath = None
            if "\n" in C3.strip():
                # means we have to wrap it in other way
                toexec = j.data.text.bash_wrap(C3)  # need to wrap a bash script to 1 line (TODO in text module)
            else:
                toexec = C3.strip()
            if self.path:
                toexec = "mkdir -p %s;cd %s;%s" % (self.path, self.path, toexec)

        elif self.interpreter == "direct":
            # means we need to execute without file unless when script
            if "\n" in C3.strip():
                tpath = self._cmd_path
                toexec = tpath
            else:
                tpath = None  # means need to execute directly
                toexec = C3.strip()

        elif self.interpreter == "bash":
            tpath = self._cmd_path + ".sh"
            toexec = "sh %s" % tpath
        elif self.interpreter in ["jumpscale", "python"]:
            tpath = self._cmd_path + ".py"
            # toexec = "python3 %s" % tpath
            if self.debug:
                toexec = "kosmos %s --debug" % tpath
            else:
                toexec = "python3 %s" % tpath
        else:
            return self._error_raise("only jumpscale or bash supported")

        if tpath:
            j.sal.fs.writeFile(tpath, C3 + "\n\n")
            j.sal.fs.chmod(tpath, 0o770)

        self.pid = 0

        if self.executor == "foreground":
            self._notify_state("running")
            j.sal.process.executeInteractive(toexec)
        elif self.executor == "background":
            self._background_start(toexec)
        elif self.executor == "tmux":
            self._tmux_start(toexec)
        elif self.executor != "corex":
            self._corex_start(toexec)
        else:
            return self._error_raise("could not find executor:'%s'" % self.executor)

        if self.executor == "foreground":
            self._notify_state("stopped")
        else:
            running = self.wait_running(die=True)
            # assert self.pid
            assert running
            self._notify_state("running")

        # if tpath:
        #     j.sal.fs.remove(tpath)

        self.save()

    @property
    def _local(self):
        if self.executor != "corex":
            return True
        return self._corex_local

    ####TMUX

    @property
    def _pane(self):
        if self._pane_ is None:
            self._pane_ = j.servers.tmux.pane_get(window=self.name, pane="main", reset=False)
        return self._pane_

    def _tmux_start(self, path):

        j.servers.tmux.server

        if "__" in self._pane.name:
            self._pane.kill()

        if self.interpreter == "bash":
            if path.startswith("sh "):
                path = path[3:]
                self._pane.execute("source %s" % path)
            elif path.startswith("bash "):
                path = path[5:]
                self._pane.execute("source %s" % path)
            else:
                raise RuntimeError()

        else:
            self._pane.execute(path)

    ####BACKGROUND

    def _background_start(self, path):
        cmd = "nohup %s >/dev/null 2>/dev/null &" % path
        self._log_debug(cmd)
        j.core.tools.execute(cmd)

    ####COREX

    @property
    def _corex_client(self):
        return j.clients.corex.get(name=self.corex_client_name)

    def _corex_start(self, path):

        if self.state == "error":
            return self._error_raise("process in error:\n%s" % p)

        if self.state == "running":
            return

        r = self._corex_client.process_start("sh %s" % path)

        self.pid = r["pid"]
        self.corex_id = r["id"]

        res = self._corex_client.process_info_get(pid=self.pid)
        assert res["pid"] == self.pid

        assert str(res["id"]) == self.corex_id

    def _corex_clean(self):
        if self.pid:
            y = self._corex_client.process_info_get(pid=self.pid)
            if y:
                assert self.pid == y["pid"]
                self.corex_id = y["id"]
            else:
                self.pid = 0
                self.state = "init"
        processlist = self._corex_client.process_list()
        for x in processlist:
            clean = False
            foundpid = False
            cmd = x["command"]
            if cmd.startswith("sh %s" % self._cmd_path):
                if x["state"] in ["stopping", "init", "crashed"]:
                    self._log_warning("found leftover", x)
                    r = self._corex_client.process_kill(x["id"])
                    j.shell()
                    clean = True
                elif x["state"] in ["running"]:
                    if not foundpid:
                        self._log_info("found process with pid:\n%s" % x)
                        self.pid = x["pid"]
                        self.corex_id = x["id"]
                        self.save()
                        foundpid = True
                    else:
                        r = self._corex_client.process_kill(x["id"])
                        clean = True
                elif x["state"] in ["stopped"]:
                    clean = True
                else:
                    j.shell()

            if cmd.strip() == "":
                self._log_info("found process with empty cmd:\n%s" % x)
                r = self._corex_client.process_kill(x["id"])
                clean = True

            if x["state"] in ["crashed"]:
                if x["error"].find("No such file") != -1:
                    r = self._corex_client.process_kill(x["id"])
                    clean = True

            if clean:
                for i in range(2):
                    r = self._corex_client.process_clean()
                    time.sleep(0.1)

    @property
    def _corex_local(self):
        if not self._corex_local_:
            self._corex_local_ = False  # FOR DEBUG
            # self._corex_local_ = self._corex_client.addr.lower() in ["localhost", "127.0.0.1"]
        return self._corex_local_

    def _corex_refresh(self):

        res = self._corex_client.process_info_get(pid=self.pid, corex_id=self.corex_id)

        def update(res, state):
            dosave = False
            if not self.data.id:
                dosave = True

            self.corex_id = res["id"]

            if self.state != state:
                self.state = state
                dosave = True

            if self.time_refresh < j.data.time.epoch - 300:
                # means we write state every 5min no matter what
                dosave = True

            if self.pid != res["pid"]:
                self.pid = res["pid"]
                dosave = True

            self.time_refresh = j.data.time.epoch

            if not self.cmd_start:
                self.cmd_start = res["command"]
                self.save()

            if dosave:
                self.save()

        if res:

            if res["state"] == "running":
                update(res, state="running")
            elif res["state"] == "stopping":
                update(res, state="stopping")
            elif res["state"] == "stopped":
                update(res, state="stopped")
            else:
                j.shell()
        else:
            self.state = "notfound"
            self.save()
