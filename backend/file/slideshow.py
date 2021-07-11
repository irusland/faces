from definitions import TIMELINE_FILE

if __name__ == "__main__":
    width = 720
    framerate = 10
    small = True
    use_codec = False
    out_file = "out.mp4"

    codec = "-vcodec libx264" if use_codec else ""
    cat = f"cat $(grep -v '^#' {TIMELINE_FILE})"
    scale = f"-filter:v scale={width}:-1" if small else ""
    cmd = f"{cat} | ffmpeg -r {framerate} -i - {scale} {codec} {out_file}"

    print(cmd)
