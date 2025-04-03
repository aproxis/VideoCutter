import subprocess
import argparse
import os
import shutil

def find_video_files(directory):
    """Find all video files under the given directory"""
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in [f for f in filenames if f.lower().endswith('.mp4')]:
            result.append(os.path.join(dirpath, f))
    return result

def get_video_duration(filename):
    """Get the duration of the video in seconds"""
    try:
        p = subprocess.Popen(["ffprobe",
                             "-loglevel",
                             "error",
                             "-select_streams",
                             "v:0",
                             "-show_entries",
                             "format=duration",
                             "-of",
                             "default=noprint_wrappers=1:nokey=1",
                             "-sexagesimal",
                             filename], stdout=subprocess.PIPE)
        (out, err) = p.communicate()
        retval = p.wait()
        if retval != 0:
            print(f"Failed to determine duration of {filename}. Skipping.")
            return None
        # Decode the bytes-like object into a string using UTF-8 encoding
        duration_str = out.decode('utf-8').strip()
        duration_parts = duration_str.split(":")
        if len(duration_parts) == 3:
            hours, minutes, seconds = map(float, duration_parts)
        else:
            minutes, seconds = map(float, duration_parts)
            hours = 0
        duration_in_seconds = hours * 3600 + minutes * 60 + seconds
        return duration_in_seconds
    except Exception as e:
        print(f"Error while getting duration of {filename}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', required=True, type=str,
                        dest='input_folder',
                        help='the input folder containing video files')
    parser.add_argument('--d', action='store_const',
                        const=True,
                        dest='is_dry_run',
                        default=False,
                        help='only show actions that would be performed')
    parser.add_argument('--m', type=int, default=None,
                        dest='minimum_duration',
                        help='delete videos shorter than N seconds')

    args = parser.parse_args()

    files_to_delete = set()
    for filename in find_video_files(args.input_folder):
        duration = get_video_duration(filename)
        if duration is not None and duration < args.minimum_duration:
            files_to_delete.add(filename)
        elif args.is_dry_run and duration is not None and duration <= args.minimum_duration:
            print(f"----- {filename} would be deleted ({duration:.3f}s)")

    if len(files_to_delete) > 0:
        if args.is_dry_run:
            print("+++++ Would delete the following files:")
        else:
            print(f"+++++ Deleted the following files shorter than {args.minimum_duration}s")
        for filename in sorted(files_to_delete):
            duration = get_video_duration(filename)
            if args.is_dry_run:
                print(f"----- {filename} ({duration:.3f}s)")
            else:
                os.unlink(filename)
                if not os.access(os.path.dirname(filename), os.R_OK | os.W_OK):
                    shutil.rmtree(os.path.dirname(filename))
                print(f"----- {filename} ({duration:.3f}s)")

if __name__ == "__main__":
    main()
