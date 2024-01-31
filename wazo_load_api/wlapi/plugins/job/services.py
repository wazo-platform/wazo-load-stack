# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import subprocess


async def run(cmd, environ):
    print(f"RECEIVED ENVIRON TYPE OF === {type(environ)}")
    for key, value in environ.items():
        if not isinstance(value, (bytes, str)):
            environ[key] = str(value)

    try:
        process = await asyncio.create_subprocess_shell(
            cmd, env=environ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        stdout_return = stdout.decode('utf-8').strip()
        stderr_return = stderr.decode('utf-8').strip()
        return_code = process.returncode
        print(f"          STDOUT ::::::::::::: {stdout_return}")
        print(f"          STDERR ::::::::::::: {stderr_return}")
        print(f"     RETURN_CODE ::::::::::::: {stderr_return}")

    except Exception as e:
        print(f"there was an error running {cmd} ::: {str(e)}")
        raise ValueError(f"Error running {cmd}: {str(e)}")

    print(f"SUCCESSFULLY RAN ::::::::::::: {cmd}")
    return {"stdout": stdout_return, "stderr": stderr_return, "returncode": return_code}
