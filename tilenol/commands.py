from functools import partial
import subprocess

from zorro.di import has_dependencies, dependency

from .event import Event
from .xcb import Core


class Events(dict):

    def __missing__(self, key):
        res = self[key] = Event('changed.'+key)
        return res


class CommandDispatcher(dict):

    def __init__(self):
        self.events = Events()

    def __setitem__(self, name, value):
        super().__setitem__(name, value)
        ev = self.events.get(name)
        if ev is not None:
            ev.emit()

    def call(self, obj, meth, *args):
        getattr(self[obj], 'cmd_' + meth)(*args)

    def callback(self, *args):
        return partial(self.call, *args)


class EnvCommands(object):

    def cmd_exec(self, *args):
        subprocess.Popen(args)

    def cmd_shell(self, *args):
        subprocess.Popen(args, shell=True)

@has_dependencies
class EmulCommands(object):

    keyregistry = dependency(object, 'key-registry')  # circ dependency
    commander = dependency(CommandDispatcher, 'commander')
    xcore = dependency(Core, 'xcore')

    def cmd_key(self, keystr):
        mod, sym = self.keyregistry.parse_key(keystr)
        code = self.xcore.keysym_to_keycode[sym][0]
        self.xcore.xtest.FakeInput(
            type=2,
            detail=code,
            time=0,
            root=self.xcore.root_window,
            rootX=0,
            rootY=0,
            deviceid=0,
            )
        self.xcore.xtest.FakeInput(
            type=3,
            detail=code,
            time=100,
            root=self.xcore.root_window,
            rootX=0,
            rootY=0,
            deviceid=0,
            )

    def cmd_button(self, num):
        num = int(num)
        self.xcore.xtest.FakeInput(
            type=4,
            detail=num,
            time=0,
            root=self.xcore.root_window,
            rootX=0,
            rootY=0,
            deviceid=0,
            )
        self.xcore.xtest.FakeInput(
            type=5,
            detail=num,
            time=30,
            root=self.xcore.root_window,
            rootX=0,
            rootY=0,
            deviceid=0,
            )



