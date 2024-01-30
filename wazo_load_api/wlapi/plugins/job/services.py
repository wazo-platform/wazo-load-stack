# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess


async def run(cmd, environ):
    print(f"RECEIVED ENVIRON TYPE OF === {type(environ)}")
    try:
        return (
            subprocess.check_output(
                cmd, env=environ, shell=True, stderr=subprocess.PIPE
            )
            .decode('utf-8')
            .strip()
        )
    except subprocess.CalledProcessError as e:
        print(f"there was an error running {cmd} ::: {str(e)}")
        raise ValueError(
            f"Error running {cmd}. stdout: '{e.stdout}'. stderr: '{e.stderr}'"
        )
