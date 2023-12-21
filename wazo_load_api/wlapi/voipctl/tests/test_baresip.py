import unittest

from modules.baresip import (
    AcceptSubCmd,
    Call,
    DialSubCmd,
    RegisterSubCmd,
    Registration,
    Shell,
)


class MockCommand(Shell):
    def __init__(self):
        self.cmd = None

    def run(self, cmd: str):
        self.cmd = cmd
        print(self.cmd)


class TestRegisterSubCmd(unittest.TestCase):
    def test_get_method(self):
        line = 1000
        stack = "example.com"
        auth_pass = "secretpassword"
        answer_mode = "manual"

        register_cmd = RegisterSubCmd(line, stack, auth_pass, answer_mode)
        expected_result = (
            f'-e "/uanew sip:{line}@{stack};'
            f'auth_pass={auth_pass};answermode={answer_mode}"'
        )
        self.assertEqual(register_cmd.get(), expected_result)

    def test_get_method_with_default_answermode(self):
        line = 1000
        stack = "example.org"
        auth_pass = "anotherpassword"

        register_cmd = RegisterSubCmd(line, stack, auth_pass)
        expected_result = (
            f'-e "/uanew sip:{line}@{stack};auth_pass={auth_pass};answermode=auto"'
        )

        self.assertEqual(register_cmd.get(), expected_result)


class TestDialSubCmd(unittest.TestCase):
    def test_get_method(self):
        callee = 2000
        stack = "example.com"

        dial_cmd = DialSubCmd(f"{callee}@{stack}")
        expected_result = f'-e "/dial {callee}@{stack}"'

        self.assertEqual(dial_cmd.get(), expected_result)


class TestAcceptSubCmd(unittest.TestCase):
    def test_get_method(self):
        accept_cmd = AcceptSubCmd()
        expected_result = '-e /accept'

        self.assertEqual(accept_cmd.get(), expected_result)


class TestBaresipCmds(unittest.TestCase):
    def __init__(self, methodName: str = "test_registration") -> None:
        super().__init__(methodName)
        self.line = 1000
        self.auth_pass = "secretpassword"
        self.stack = "example.org"
        self.callee = 20000
        self.timeout = 60
        self.command = MockCommand()
        self.answermode = "auto"

    def test_registration(self):
        expected_output = (
            'baresip -t 60 -f /root/.baresip'
            '-e "/uanew sip:1000@example.org;'
            'auth_pass=secretpassword;answermode=auto"'
        )
        registration = Registration(
            line=self.line,
            auth_pass=self.auth_pass,
            stack=self.stack,
            command=self.command,
            timeout=self.timeout,
            answermode=self.answermode,
        )
        self.assertEqual(registration.cmd, expected_output)

    def test_call(self):
        expected_output = (
            'baresip -t 60 -f /root/.baresip'
            '-e "/uanew sip:1000@example.org;auth_pass=secretpassword;answermode=auto"'
            '-e "/dial 20000@example.org"'
        )
        call = Call(
            line=self.line,
            stack=self.stack,
            auth_pass=self.auth_pass,
            callee=str(self.callee),
            command=self.command,
            timeout=self.timeout,
        )
        self.assertEqual(call.cmd, expected_output)
