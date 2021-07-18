from definitions import TIMELINE_FILE


def _debug():
    width = 240
    framerate = 10
    small = True
    out_file = "debug.mp4"
    timeline_dir = "/Users/irusland/LocalProjects/faces_data/timeline/"

    scale = f"scale={width}:-1" if small else ""
    numbers = (
        "drawtext=fontfile=Arial.ttf: text='%{frame_num}': "
        "start_number=0: x=(w-tw)/2: y=h-(2*lh): fontcolor=black: "
        "fontsize=20: box=1: boxcolor=white: boxborderw=5"
    )
    input_ = f"{timeline_dir}%04d.jpg"

    filter_ = f'-vf "{", ".join([scale, numbers])}"'
    cmd = f"ffmpeg -r {framerate} -i {input_} {filter_} {out_file}"

    return cmd


def main():
    width = 1440
    framerate = 10
    small = True
    use_codec = False
    out_file = "out.mp4"

    codec = "-vcodec libx264" if use_codec else ""
    cat = f"cat $(grep -v '^#' {TIMELINE_FILE})"
    scale = f"-filter:v scale={width}:-1" if small else ""
    cmd = f"{cat} | ffmpeg -r {framerate} -i - {scale} {codec} {out_file}"
    return cmd


if __name__ == "__main__":
    print('To save debug enter "d"')
    if input() == "d":
        print(_debug())
    else:
        print(main())
