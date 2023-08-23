# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

async def run(cmd):
    print(cmd)
    try:
        return  subprocess.check_output(cmd, shell=True, 
                                stderr=subprocess.PIPE).decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"Error running {cmd}. stdout: '{e.stdout}'. stderr: '{e.stderr}'")
