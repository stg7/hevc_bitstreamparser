#!/bin/bash
# This file is part of hevc_parser.
# hevc_parser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# hevc_parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with hevc_parser. If not, see <http://www.gnu.org/licenses/>.

requirements() {
    sudo apt-get update -qq

    sudo apt-get -y install autoconf automake build-essential cmake git \
        libass-dev libfreetype6-dev libsdl2-dev libtheora-dev libtool \
        libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
        libxcb-xfixes0-dev mercurial pkg-config texinfo wget \
        zlib1g-dev yasm
        # exclude those dependencies to remove external decoding parts
        #libx264-dev libx265-dev libvpx-dev
}

requirements

cd ffmpeg-4.1

echo "configure ffmpeg"
./configure --pkg-config-flags="--static" \
  --disable-doc \
  --enable-pthreads \
  --enable-debug=2 \
  --disable-nvenc \
  --disable-libx265 \
  --enable-decoder=hevc \
  --enable-parser=hevc \
  --enable-demuxer=hevc \
  --disable-vaapi

make -j 12