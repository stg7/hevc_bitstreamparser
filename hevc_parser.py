#!/usr/bin/env python3
import argparse
import json
import sys
import subprocess
import os
import bz2
import gzip
import logging


def file_open(filename, mode="r"):
    """ Open a file, and if you add bz2 to filename a compressed file will be opened
    """
    if "bz2" in filename:
        return bz2.open(filename, mode + "t")
    if "gz" in filename:
        return gzip.open(filename, mode + "t")
    return open(filename, mode)


def shell_call(call):
    """
    Run a program via system call and return stdout + stderr.
    @param call programm and command line parameter list, e.g ["ls", "/"]
    @return stdout and stderr of programm call
    """
    try:
        output = subprocess.check_output(call, universal_newlines=True, shell=True)
    except Exception as e:
        output = str(e.output)
    return output


def assert_file(filename, error_msg):
    if not os.path.isfile(filename):
        logging.error(error_msg)
        raise Exception()


def parse_video(video_file):
    ffprobe = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ffmpeg-4.1", "ffprobe"))
    assert_file(ffprobe, "local patched ffprobe could not be found, please compile everything first using prepare.sh")
    cmd = f""" {ffprobe} -v error -show_format -select_streams v:0 -show_frames -show_entries stream=bit_rate,width,height,avg_frame_rate,codec_name -show_entries frame=key_frame,pkt_size,pict_type -of json "{video_file}" """
    res = shell_call(cmd).split("\n")
    current_values = []
    grouped_qp_values = []
    remaining = []
    for l in res:
        if "start_frame" in l:  # frame start indication
            if current_values != []:
                grouped_qp_values.append(current_values)
                current_values = []
            continue
        if "qp=" in l:
            # its a qp=.. line
            current_values.append(int(l.split("=")[1].strip()))
        else:
            remaining.append(l)

    grouped_qp_values.append(current_values)

    def clean_str(r):
        return r.split(":")[1].split(",")[0].replace("\"", "").strip()

    # frame stats
    key_frames = []
    pkt_sizes = []
    pict_types = []
    bit_rate = "unknown"
    width = "unknown"
    height = "unknown"
    avg_frame_rate = "unknown"
    codec_name = "unknown"

    for r in remaining:
        if "key_frame" in r:
            key_frames.append(int(clean_str(r)))
        if "pkt_size" in r:
            pkt_sizes.append(int(clean_str(r)))
        if "pict_type" in r:
            pict_types.append(clean_str(r))
        if "bit_rate" in r:
            bit_rate = int(clean_str(r))
        if "width" in r:
            width = int(clean_str(r))
        if "height" in r:
            height = int(clean_str(r))
        if "avg_frame_rate" in r:
            avg_frame_rate = clean_str(r)
        if "codec_name" in r:
            codec_name = clean_str(r)

    per_frame = []
    for i, g in enumerate(grouped_qp_values):
        per_frame.append({
            "mean_qp": sum(g) / len(g),
            "min_qp": min(g),
            "max_qp": max(g),
            "pkt_size": pkt_sizes[i],
            "key_frame": key_frames[i],
            "pict_type": pict_types[i]
        })
    return {
        "per_frame": per_frame,
        "bit_rate": bit_rate,
        "width": width,
        "height": height,
        "avg_frame_rate": avg_frame_rate,
        "codec_name": codec_name
    }

def main(_):
    # argument parsing
    parser = argparse.ArgumentParser(description='extract qp values from hevc encoded videos',
                                     epilog="stg7 2019",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video_file", type=str, help="input video file")
    parser.add_argument("--report_file", type=str, default="report.json.bz2", help="file to store the report, supports compression, e.g. using report.bz2")
    parser.add_argument("--nostdout", action="store_true", help="no report output on stdout")

    a = vars(parser.parse_args())

    report = parse_video(a["video_file"])
    if a["report_file"] is None or not a["nostdout"]:
        print(json.dumps(report, indent=4))
    if a["report_file"] is not None:
        with file_open(a["report_file"], "w") as rfp:
            json.dump(report, rfp, indent=4)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

