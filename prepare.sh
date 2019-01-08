#!/bin/bash

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