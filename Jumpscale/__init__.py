import os
import socket
import pytoml
import sys
from importlib import util
os.environ["LC_ALL"]='en_US.UTF-8'

def tcpPortConnectionTest(ipaddr, port, timeout=None):
    conn = None
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            conn.settimeout(timeout)
        try:
            conn.connect((ipaddr, port))
        except BaseException:
            return False
    finally:
        if conn:
            conn.close()
    return True

def profileStart():
    import cProfile
    pr = cProfile.Profile()
    pr.enable()
    return pr

def profileStop(pr):
    pr.disable()
    import io
    import pstats
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

# pr=profileStart()


class Core():
    def __init__(self,j):
        self._db = None
        self._dir_home = None
        self._dir_jumpscaleX = None
        self._isSandbox = None


    @property
    def db(self):
        if not self._db:
            # if tcpPortConnectionTest("localhost", 6379):
            try:
                from redis import StrictRedis
                # print("CORE_REDIS")
                if self.isSandbox:
                    self._db = StrictRedis(unix_socket_path='/sandbox/var/redis.sock', db=0)
                else:
                    self._db = StrictRedis(host='localhost', port=6379, db=0)
                self._db.get("jumpscale.config")
                self._db_fakeredis = False
            except Exception as e:
                # print("CORE_MEMREDIS")
                import fakeredis
                self._db = fakeredis.FakeStrictRedis()
                self._db_fakeredis = True
        return self._db

    def db_reset(self):
        if hasattr(j.data,"cache"):
            j.data.cache._cache = {}
        self._db = None

    @property
    def dir_jumpscaleX(self):
        if self._dir_jumpscaleX is None:
            self._dir_jumpscaleX = os.path.dirname(os.path.dirname(__file__))
        return self._dir_jumpscaleX

    @property
    def isSandbox(self):
        if self._isSandbox is None:
            if self.dir_jumpscaleX.startswith("/sandbox"):
                self._isSandbox = True
            else:
                self._isSandbox = False
        return self._isSandbox


class Jumpscale():

    def __init__(self):
        self._shell = None
        self.exceptions = None

    def shell(self,name="",loc=True):
        if self._shell == None:
            from IPython.terminal.embed import InteractiveShellEmbed
            if name is not "":
                name = "SHELL:%s" % name
            self._shell = InteractiveShellEmbed(banner1= name, exit_msg="")
        if loc:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            f = calframe[1]
            print("\n*** file: %s"%f.filename)
            print("*** function: %s [linenr:%s]\n" % (f.function,f.lineno))
        return self._shell(stack_depth=2)

    def debug(self):
        import urwid
        urwid.set_encoding("utf8")
        from pudb import set_trace; set_trace()




j = Jumpscale()
j.core = Core(j)
j.core._groups = {}


rootdir = os.path.dirname(os.path.abspath(__file__))
# print("- setup root directory: %s" % rootdir)

spec = util.spec_from_file_location("IT", "/%s/core/InstallTools.py"%os.path.dirname(__file__))


from .core.InstallTools import MyEnv
from .core.InstallTools import UbuntuInstall
from .core.InstallTools import JumpscaleInstaller
from .core.InstallTools import Tools


j.core.myenv = MyEnv
j.core.myenv._init()



j.core.installer_ubuntu = UbuntuInstall
j.core.installer_jumpscale = JumpscaleInstaller()
j.core.tools = Tools

j._profileStart = profileStart
j._profileStop = profileStop

# pr=profileStart()

from .core.Text import Text
j.core.text = Text(j)

from .core.Dirs import Dirs
j.dirs = Dirs(j)
j.core.dirs = j.dirs

from .core.logging.LoggerFactory import LoggerFactory
j.logger = LoggerFactory(j)
j.core.logger = j.logger

from .core.Application import Application
j.application = Application(j)
j.core.application = j.application

from .core.cache.Cache import Cache
j.core.cache = Cache(j)

from .core.PlatformTypes import PlatformTypes
j.core.platformtype = PlatformTypes(j)

from .core.errorhandler.ErrorHandler import ErrorHandler
j.errorhandler = ErrorHandler(j)
j.core.errorhandler = j.errorhandler
j.exceptions = j.errorhandler.exceptions
j.core.exceptions = j.exceptions


#THIS SHOULD BE THE END OF OUR CORE, EVERYTHING AFTER THIS SHOULD BE LOADED DYNAMICALLY

j.core.application._lib_generation_path = j.core.tools.text_replace("{DIR_BASE}/lib/jumpscale/Jumpscale/jumpscale_generated.py")

if "JSRELOAD" in os.environ  and os.path.exists(j.core.application._lib_generation_path):
    print("RELOAD JUMPSCALE LIBS")
    os.remove(j.core.application._lib_generation_path)

generated = False
# print (sys.path)
if not os.path.exists(j.core.application._lib_generation_path):
    print("WARNING: GENERATION OF METADATA FOR JUMPSCALE")
    from .core.generator.JSGenerator import JSGenerator
    j.core.jsgenerator = JSGenerator(j)
    j.core.jsgenerator.generate(methods_find=True)
    j.core.jsgenerator.report()
    generated = True

ipath = j.core.tools.text_replace("{DIR_BASE}/lib/jumpscale/Jumpscale")
if ipath not in sys.path:
    sys.path.append(ipath)

import jumpscale_generated

if generated  and len(j.core.application.errors_init)>0:
    print("THERE ARE ERRORS: look in /tmp/jumpscale/ERRORS_report.md")
# else:
#     print ("INIT DONE")

# profileStop(pr)

# j.shell()

# import time
# time.sleep(1000)



# ssh = j.clients.ssh.instances
# iyo = j.clients.itsyouonline.instances
# zos = j.kosmos.zos.instances

