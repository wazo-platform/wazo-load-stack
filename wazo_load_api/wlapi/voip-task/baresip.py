from abc import ABC, abstractmethod
import os
import subprocess


class Shell(ABC):
    @abstractmethod
    def run(self, cmd):
        pass

class Command(Shell):
    """Command class implements the Shell abstract class
    and allows to execute a shell command."""
    def run(self, cmd:str):
        environ = os.environ
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
    def __init__(self, line:int, stack:str, auth_pass:str, answermode:str = "auto") -> None:
        self.line:int = line
        self.stack:str = stack
        self.auth_pass:str = auth_pass
        self.answer_mode:str = answermode

    def get(self) -> str:
        return f'-e "/uanew sip:{self.line}@{self.stack};auth_pass={self.auth_pass};answermode={self.answer_mode}"'

class DialSubCmd(BaresipSubCmd):
    """ DialSubCmd class implements BaresipSubCmd and returns
    the baresip subcommand for dialing a contact.
    It takes the following parameters:
     - callee: (integer) The line to call
     - stack: (string) The stack where to call
    """
    def __init__(self, callee:int, stack:str) -> None:
        self.callee:int = callee
        self.stack:str = stack

    def get(self) -> str:
        return f'-e "/dial {self.callee}@{self.stack}"'

class AcceptSubCmd(BaresipSubCmd):
    """ AcceptSubCmd implements BaresipSubCmd and returns
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
    def __init__(self, line:int, auth_pass:str, 
                 stack:str, command:Shell, 
                 answermode:str = "auto", timeout:int = 60) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.answermode = answermode
        self.register:BaresipSubCmd = RegisterSubCmd(
            line=self.line,
            stack=self.stack,
            auth_pass=self.auth_pass,
            answermode=self.answermode
            ).get()
        self.timeout:int = timeout
        self.cmd:str = f"baresip -t {self.timeout} -f /root/.baresip {self.register}"
        self.shell:Shell = command

    def run(self) -> None:
       self.shell.run(self.cmd)

class Call(BaresipCmd):
    """Call class implements BaresipCmd and will
    execute a registration followed by a call.
    It takes the following parameters:
     - line: (integer) is the account that will authenticate for registration
     - stack: (string) is the stack where to register
     - auth_pass: (string) is the password associated to the line
     - callee: (integer) the contact to call (ex: 1001@example.com)
     - command: (Shell) instance of a Shell class that will be use to run the command.
     - timeout: (integer) timeout after that will terminate the baresip command.
    """
    def __init__(self, line:int, stack:str, 
                 auth_pass:str, callee:int, 
                 command:Shell, timeout:int = 60) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.callee:int = callee
        self.timeout:int = timeout
        self.register:BaresipSubCmd = RegisterSubCmd(self.line, self.stack, self.auth_pass).get()
        self.dial:BaresipSubCmd = DialSubCmd(self.callee, self.stack).get()
        self.cmd:str = f"baresip -t {self.timeout} -f /root/.baresip {self.register} {self.dial}"
        self.shell:Shell = command

    def run(self) ->  None:
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
    def __init__(self,line:int, stack:str, 
                 auth_pass:str, command:Shell, 
                 answermode:str = "auto", timeout:int = 300) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.timeout:int = timeout
        self.answermode:str = answermode

        self.register:BaresipSubCmd = RegisterSubCmd(
            line=self.line, 
            stack=self.stack, 
            auth_pass=self.auth_pass,
            answermode=self.answermode
            ).get()

        self.accept:BaresipSubCmd = AcceptSubCmd().get()

        self.cmd:str = f"baresip -t {self.timeout} -f /root/.baresip {self.register} {self.accept}"
        self.shell:Shell = command

    def run(self) -> None:
        self.shell.run(self.cmd)


class Caller:
    """ 
    Caller class is used to figure out whether or not a line
    is a caller or a callee. A caller is an odd line number while 
    a callee is an even line number. This rule was arbitrarily defined 
    for the load framework.
    """
    def __init__(self, line:int):
        self.line:int = line

    def is_caller(self) -> bool:
        if self.line % 2  == 0:
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
    def __init__(self, line:int, auth_pass:str, 
                 stack:str, timeout:int = 60) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.answermode:str = "auto"
        self.timeout:int = timeout
        self.shell:Shell = Command() 
        self.scenario:BaresipCmd = Registration(
            line=self.line,
            auth_pass=self.auth_pass,
            stack=self.stack,
            command=self.shell,
            answermode=self.answermode,
            timeout=self.timeout
            )
    
    def run_scenario(self) -> None:
        self.scenario.run()

class AutoCall(Scenario):
    """AutoCall scenario is a simple call to *10."""
    def __init__(self, line:int, auth_pass:str, 
                 stack:str, callee:int = 10, 
                 timeout:int = 60) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.callee:int = f"*{callee}"
        self.answermode:str = "auto"
        self.timeout:int = timeout
        self.shell:Shell = Command() 
        self.scenario:BaresipCmd = Call(
            line=self.line, 
            auth_pass=self.auth_pass,
            stack = self.stack,
            callee= self.callee,
            command=self.shell,
            answermode=self.answermode,
            timeout=self.timeout
            )

    def run_scenario(self) -> None:
        self.scenario.run()

class SimpleCall(Scenario):
    """SimpleCall implements a call to a specific callee."""
    def __init__(self, line:int, auth_pass:str, 
                 callee:int, stack:str, 
                 timeout:int = 60) -> None:
        self.line:int = line
        self.auth_pass:str = auth_pass
        self.stack:str = stack
        self.answermode:str = "auto"
        self.callee:str = str(callee)
        self.timeout:int = timeout
        self.shell:Shell = Command() 

        if Caller(self.line).is_caller():
            self.scenario:BaresipCmd = Call(
                line=self.line, 
                auth_pass=self.auth_pass,
                stack = self.stack,
                callee= self.callee,
                command=self.shell,
                answermode=self.answermode,
                timeout=self.timeout
                )
        else:
            self.scenario:BaresipCmd = Accept(
                line=self.line, 
                auth_pass=self.auth_pass,
                stack = self.stack,
                command=self.shell,
                answermode=self.answermode,
                timeout=self.timeout
                )

    def run_scenario(self) -> None:
        self.scenario.run()


class ProcessJob():

    def __init__(self, baresip:str = "/usr/bin/baresip", use_case:str = "simple_call") -> None:
        self.baresip_path:str = baresip
        self.scenario = self._new_scenario()
        self.shell = Command()
        self.line = os.getenv("LINE")
        self.stack = os.getenv("STACK")
        self.password = os.getenv("PASSWORD")
        self.use_case = os.getenv("SCENARIO", use_case)
        self.timeout = os.getenv("CALL_DURATION")
        self.callee = os.getenv("GROUP_CALL")

    def _new_scenario(self) -> Scenario:
        scenarios = {
            "registration_only": RegistrationOnly(
                line=self.line,
                auth_pass=self.password,
                stack=self.stack,
                timeout=self.timeout
            ),
            "auto_call": AutoCall(
                line=self.line,
                auth_pass=self.password,
                stack=self.stack,
                timeout=self.timeout
            ),
            "simple_call": SimpleCall(
                line=self.line,
                auth_pass=self.password,
                stack=self.stack,
                timeout=self.timeout,
                callee=self.callee
            )
        }
        return scenarios[self.use_case]

    def run(self):
        self.scenario.run_scenario()

    