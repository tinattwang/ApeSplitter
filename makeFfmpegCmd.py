#
# makeFfmpegCmd.py for generating the commands for slicing APE file to MP3 files.
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

def makeFfmpegCmd(file):
    d  = open(file).read().splitlines()
    general = {}
    tracks = []
    current_file = None
    path = os.path.split(file)[0]
    cmds = []

    for line in d:
        if line.startswith('REM GENRE '):
            general['genre'] = ' '.join(line.split(' ')[2:])
        if line.startswith('REM DATE '):
            general['date'] = ' '.join(line.split(' ')[2:])
        if line.startswith('PERFORMER '):
            general['artist'] = ' '.join(line.split(' ')[1:]).replace('"', '')
        if line.startswith('TITLE '):
            general['album'] = ' '.join(line.split(' ')[1:]).replace('"', '')
        if line.startswith('FILE '):
            current_file = os.path.join(path, ' '.join(line.split(' ')[1:-1]).replace('"', ''))

        if line.startswith('  TRACK '):
            track = general.copy()
            track['track'] = int(line.strip().split(' ')[1], 10)

            tracks.append(track)

        if line.startswith('    TITLE '):
            tracks[-1]['title'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
        if line.startswith('    PERFORMER '):
            tracks[-1]['artist'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
        if line.startswith('    INDEX 01 '):
            t = list(map(int, ' '.join(line.strip().split(' ')[2:]).replace('"', '').split(':')))
            tracks[-1]['start'] = 60 * t[0] + t[1] + t[2] / 100.0

    for i in range(len(tracks)):
        if i != len(tracks) - 1:
            tracks[i]['duration'] = tracks[i + 1]['start'] - tracks[i]['start']

    for track in tracks:
        metadata = {
            'artist': track['artist'],
            'title': track['title'],
            'album': track['album'],
            'track': str(track['track']) + '/' + str(len(tracks))
        }

        if 'genre' in track:
            metadata['genre'] = track['genre']
        if 'date' in track:
            metadata['date'] = track['date']

        cmd = 'ffmpeg'
        cmd += ' -i "%s"' % current_file
        cmd += ' -b:a 320k'
        cmd += ' -ss %.2d:%.2d:%.2d' % (track['start'] / 60 / 60, track['start'] / 60 % 60, int(track['start'] % 60))

        if 'duration' in track:
            cmd += ' -t %.2d:%.2d:%.2d' % (
                track['duration'] / 60 / 60, track['duration'] / 60 % 60, int(track['duration'] % 60))

        cmd += ' ' + ' '.join('-metadata %s="%s"' % (k, v) for (k, v) in metadata.items())
        cmd += ' "%s/%.2d - %s - %s.mp3"' % (path, track['track'], track['artist'], track['title'])

        cmds.append(cmd)
    return cmds
