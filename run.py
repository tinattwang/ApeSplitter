#
# run.py for running ffmpeg commands by multiprocessing
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Wang Tiantian

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import time
import multiprocessing
import subprocess
import makeFfmpegCmd
import fnmatch
import sys

def splitApe(srcFile, errorCallback, param):
    if not isinstance(param, dict):
        param = {}

    param['src']        = srcFile
    param['exitCode']   = ""

    if not os.path.exists(srcFile):
        param['exitCode'] += "1001"
        errorCallback(param)
        return
    if not callable(errorCallback):
        errorCallback = print
        param['exitCode'] += "1002"
        errorCallback(param)
        return

    cmds        = makeFfmpegCmd.makeFfmpegCmd(srcFile)
    cpu_count   = multiprocessing.cpu_count()
    maxProcess  = cpu_count * 3 // 4
    output      = os.popen('ps aux |grep ffmpeg | grep -v grep | wc -l')
    curProcess  = int(output.read())

    while True:
        if maxProcess > curProcess:
            for cmd in cmds:
                process         = subprocess.Popen(cmd, shell = True,
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE)
                stdout, stderr  = process.communicate()
                process.wait()
                exitCode        = process.returncode

                if exitCode != 0 and callable(errorCallback):
                    param["srcFile"]     = srcFile
                    param["cmd"]         = cmd
                    param["exitCode"]    = exitCode
                    errorCallback(param)
            break

        output     = os.popen('ps aux |grep ffmpeg | grep -v grep | wc -l')
        curProcess = int(output.read())

        time.sleep(5)


def splitDir(dir):
    def _print(dict):
        for key, value in dict.items():
            print("[ error: ] %s : %s"%(key, value))
    param   = {}
    matches = []

    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.cue'):
            matches.append(os.path.join(root, filename))

    for file in matches:
        splitApe(file, _print, param)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit()
    dir = sys.argv[1]
    splitDir(dir)
