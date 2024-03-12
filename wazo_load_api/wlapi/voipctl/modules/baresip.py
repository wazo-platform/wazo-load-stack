import os
import subprocess
from abc import ABC, abstractmethod
from typing import cast


def strace_debugger(func):
    def wrapper(*args, **kwargs):
        instance = args[0]
        if instance.trace:
            cmd = (
                f"strace -o /opt/voipctl/debug/baresip.log --output-separately "
                f"{func(*args, **kwargs)}"
            )
        else:
            cmd = func(*args, **kwargs)
        return cmd

    return wrapper


class Shell(ABC):
    @abstractmethod
    def run(self, cmd):
        pass


class Command(Shell):
    """Command class implements the Shell abstract class
    and allows to execute a shell command."""

    def run(self, cmd: str):
        environ = os.environ
        print(cmd)
        try:
            return (
                subprocess.check_output(
                    cmd, env=environ, shell=True, stderr=subprocess.PIPE
                )
                .decode('utf-8')
                .strip()
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Error running {cmd}. stdout: '{e.stdout}'. stderr: '{e.stderr}'"
            )


class BaresipSubCmd(ABC):
    @abstractmethod
    def get(self) -> str:
        pass


class RegisterSubCmd(BaresipSubCmd):
    """RegisterSubCmd implements BaresipSubCmd and returns
    the uanew subcommand used for baresip to register.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - answermode: (string) answermode for incoming call. Default auto.
                    valide values: manual,early,auto,early-audio,early-video
    """

    def __init__(
        self,
        line: int,
        stack: str,
        auth_pass: str,
        answermode: str = "auto",
        enable_strace: bool = False,
    ) -> None:
        self.line: int = line
        self.stack: str = stack
        self.auth_pass: str = auth_pass
        self.answer_mode: str = answermode
        self.mediaenc: str = "dtls_srtp"
        self.audio_source: str = "aufile,/opt/Rameses.wav"

    def get(self) -> str:
        return (
            f'-e "/uanew sip:{self.line}@{self.stack};'
            f'auth_pass={self.auth_pass};audio_source={self.audio_source};'
            f'mediaenc={self.mediaenc};answermode={self.answer_mode}"'
        )


class DialSubCmd(BaresipSubCmd):
    """DialSubCmd class implements BaresipSubCmd and returns
    the baresip subcommand for dialing a contact.
    It takes the following parameters:
     - callee: (string) The line to call
    """

    def __init__(self, callee: str) -> None:
        self.callee: str = callee

    def get(self) -> str:
        return f'-e "/dial {self.callee}"'


class AcceptSubCmd(BaresipSubCmd):
    """AcceptSubCmd implements BaresipSubCmd and returns
    the baresip subcommand for accepting a call.
    """

    def get(self) -> str:
        return "-e /accept"


class BaresipCmd(ABC):
    @abstractmethod
    def run(self):
        pass


class Registration(BaresipCmd):
    """Registration class implements BaresipCmd and will
    execute a registration.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - command: (Shell) instance of a Shell class that will be use to run the command.
     - timeout: (integer) timeout after that will terminate the baresip command.
    """

    def __init__(
        self,
        line: int,
        auth_pass: str,
        stack: str,
        command: Shell,
        answermode: str = "auto",
        timeout: int = 60,
    ) -> None:
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.answermode = answermode
        self.register = RegisterSubCmd(
            line=self.line,
            stack=self.stack,
            auth_pass=self.auth_pass,
            answermode=self.answermode,
        )
        self.timeout: int = timeout
        self.cmd: str = self.get()
        self.shell: Shell = command

    @strace_debugger
    def get(self):
        return f"/usr/local/bin/baresip -t {self.timeout} -f /root/.baresip {self.register.get()}"

    def run(self) -> None:
        print(self.cmd)
        self.shell.run(self.cmd)


class Call(BaresipCmd):
    """Call class implements BaresipCmd and will
    execute a registration followed by a call.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - callee: (string) the contact to call (ex: 1001@example.com)
     - command: (Shell) instance of a Shell class that will be use to run the command.
     - timeout: (integer) timeout after that will terminate the baresip command.
    """

    def __init__(
        self,
        line: int,
        stack: str,
        auth_pass: str,
        callee: str,
        command: Shell,
        timeout: int = 60,
        trace: bool = False,
    ) -> None:
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.callee: str = f'{callee}@{self.stack}'
        self.timeout: int = timeout
        self.register: str = RegisterSubCmd(self.line, self.stack, self.auth_pass).get()
        self.dial: str = DialSubCmd(self.callee).get()
        self.trace = trace
        self.cmd: str = self.get()
        self.shell: Shell = command

    @strace_debugger
    def get(self):
        return (
            f"/usr/local/bin/baresip -t {self.timeout} "
            f"-f /root/.baresip {self.register} {self.dial}"
        )

    def run(self) -> None:
        self.shell.run(self.cmd)


class Accept(BaresipCmd):
    """Accept class implements BaresipCmd and will
    accept a call.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - command: (Shell) instance of a Shell class that will be use to run the command.
     - timeout: (integer) timeout after that will terminate the baresip command.
    """

    def __init__(
        self,
        line: int,
        stack: str,
        auth_pass: str,
        command: Shell,
        answermode: str = "auto",
        timeout: int = 300,
        trace: bool = False,
    ) -> None:
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.timeout: int = timeout
        self.answermode: str = answermode
        self.trace = trace

        self.register: str = RegisterSubCmd(
            line=self.line,
            stack=self.stack,
            auth_pass=self.auth_pass,
            answermode=self.answermode,
        ).get()

        self.accept: str = AcceptSubCmd().get()

        self.cmd: str = self.get()
        self.shell: Shell = command

    @strace_debugger
    def get(self):
        return (
            f"/usr/local/bin/baresip -t {self.timeout} "
            "-f /root/.baresip {self.register} {self.accept}"
        )

    def run(self) -> None:
        self.shell.run(self.cmd)


class Caller:
    """
    Caller class is used to figure out whether or not a line
    is a caller or a callee. A caller is an odd line number while
    a callee is an even line number. This rule was arbitrarily defined
    for the load framework.
    """

    def __init__(self, line: int):
        self.line: int = int(line)

    def is_caller(self) -> bool:
        if self.line % 2 == 0:
            return True
        return False


class Scenario(ABC):
    @abstractmethod
    def run_scenario(self):
        pass


class RegistrationOnly(Scenario):
    """RegistrationOnly implements a Scenario.
    It will just perform a registration.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - timeout: (integer) timeout after the baresip command will terminate.
    """

    def __init__(
        self,
        line: int,
        auth_pass: str,
        stack: str,
        timeout: int = 60,
        trace: bool = False,
    ) -> None:
        print("=========== REGISTRATION ONLY =========")
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.answermode: str = "auto"
        self.timeout: int = timeout
        self.shell: Shell = Command()
        self.scenario: BaresipCmd = Registration(
            line=self.line,
            auth_pass=self.auth_pass,
            stack=self.stack,
            command=self.shell,
            answermode=self.answermode,
            timeout=self.timeout,
        )

    def run_scenario(self) -> None:
        print("=========== REGISTRATION ONLY RUN =========")
        self.scenario.run()


class AutoCall(Scenario):
    """AutoCall scenario is a simple call to *10."""

    def __init__(
        self,
        line: int,
        auth_pass: str,
        stack: str,
        callee: int = 10,
        timeout: int = 60,
        trace: bool = False,
    ) -> None:
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.callee: str = f"*{callee}"
        self.answermode: str = "auto"
        self.timeout: int = timeout
        self.trace = trace
        self.shell: Shell = Command()
        self.scenario: BaresipCmd = Call(
            line=self.line,
            auth_pass=self.auth_pass,
            stack=self.stack,
            callee=self.callee,
            command=self.shell,
            timeout=self.timeout,
            trace=self.trace,
        )

    def run_scenario(self) -> None:
        self.scenario.run()


class SimpleCall(Scenario):
    """SimpleCall implements a call to a specific callee."""

    def __init__(
        self,
        line: int,
        auth_pass: str,
        callee: int,
        stack: str,
        timeout: int = 60,
        trace: bool = False,
    ) -> None:
        self.line: int = line
        self.auth_pass: str = auth_pass
        self.stack: str = stack
        self.answermode: str = "auto"
        self.callee: str = f'{callee}'
        self.timeout: int = timeout
        self.trace = trace
        self.shell: Shell = Command()

        if Caller(self.line).is_caller():
            self.scenario = cast(
                BaresipCmd,
                Call(
                    line=self.line,
                    auth_pass=self.auth_pass,
                    stack=self.stack,
                    callee=self.callee,
                    command=self.shell,
                    timeout=self.timeout,
                    trace=self.trace,
                ),
            )
        else:
            self.scenario = cast(
                BaresipCmd,
                Accept(
                    line=self.line,
                    auth_pass=self.auth_pass,
                    stack=self.stack,
                    command=self.shell,
                    answermode=self.answermode,
                    timeout=self.timeout,
                    trace=self.trace,
                ),
            )

    def run_scenario(self) -> None:
        self.scenario.run()


class ProcessJob:
    def __init__(self, baresip: str = "/usr/bin/baresip") -> None:
        self.baresip_path: str = baresip
        self.shell = Command()
        self.line = os.getenv("LINE")
        self.stack = os.getenv("STACK")
        self.password = os.getenv("PASSWORD")
        self.use_case = os.getenv("SCENARIO")
        self.timeout = os.getenv("CALL_DURATION")
        self.callee = os.getenv("GROUP_CALL")
        self.debug = os.getenv("DEBUG")
        print(f"DEBUG IS {self.debug}")
        self.trace = False
        if self.debug == "True" or self.debug == "true":
            self.trace = True
        print(f"TRACE IS {self.trace}")
        print(self.use_case)
        self.scenario = self._new_scenario()

    def _new_scenario(self) -> Scenario:
        if self.use_case == "registration_only":
            scenario = cast(
                Scenario,
                RegistrationOnly(
                    line=cast(int, self.line),
                    auth_pass=cast(str, self.password),
                    stack=cast(str, self.stack),
                    timeout=cast(int, self.timeout),
                    trace=self.trace,
                ),
            )
        if self.use_case == "auto_call":
            scenario = cast(
                Scenario,
                AutoCall(
                    line=cast(int, self.line),
                    auth_pass=cast(str, self.password),
                    stack=cast(str, self.stack),
                    timeout=cast(int, self.timeout),
                    trace=self.trace,
                ),
            )
        if self.use_case == "simple_call":
            scenario = cast(
                Scenario,
                SimpleCall(
                    line=cast(int, self.line),
                    auth_pass=cast(str, self.password),
                    stack=cast(str, self.stack),
                    timeout=cast(int, self.timeout),
                    callee=cast(int, self.callee),
                    trace=self.trace,
                ),
            )
        return scenario

    def run(self):
        self.scenario.run_scenario()


def main():
    ProcessJob().run()
