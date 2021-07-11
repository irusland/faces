import ffmpeg

if __name__ == "__main__":
    dir(ffmpeg)
    "cat *.jpg | ffmpeg -r 10 -i - -filter:v scale=720:-1 out2.mp4"
