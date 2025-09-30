import argparse
from pathlib import Path
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Join videos from Video folder, add captions from Caption folder, and mix BGM from BGM folder."
    )
    p.add_argument("--video-dir", type=Path, default=Path("Video"), help="Folder with input videos")
    p.add_argument("--caption-dir", type=Path, default=Path("Caption"), help="Folder with .srt captions")
    p.add_argument("--bgm-dir", type=Path, default=Path("BGM"), help="Folder with background music tracks")
    p.add_argument("--output-dir", type=Path, default=Path("Output"), help="Folder to write outputs")
    p.add_argument("--output", type=Path, default=None, help="Output video filename (defaults to Output/merged.mp4)")
    p.add_argument("--exts", nargs="*", default=[".mp4", ".mov", ".mkv", ".avi"], help="Video extensions to include")
    p.add_argument("--bgm-file", type=Path, default=None, help="Specific BGM file to use (overrides dir scan)")
    p.add_argument("--bgm-volume", type=float, default=0.15, help="BGM volume (0.0-1.0)")
    p.add_argument("--no-soft-subs", action="store_true", help="Burn-in subtitles instead of embedding as soft track")
    # Alias for clarity
    p.add_argument("--burn-in", dest="no_soft_subs", action="store_true", help="Alias of --no-soft-subs")
    p.add_argument("--generate-captions", action="store_true", help="Use Google Speech-to-Text if SRTs missing")
    p.add_argument("--language", default="en-US", help="Language code for STT if generating captions")
    p.add_argument("--sample-rate", type=int, default=16000, help="Sample rate for STT audio")
    p.add_argument("--keep-temp", action="store_true", help="Keep temporary files for debugging")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    run_pipeline(
        video_dir=args.video_dir,
        caption_dir=args.caption_dir,
        bgm_dir=args.bgm_dir,
        output_dir=args.output_dir,
        output_file=args.output,
        exts=args.exts,
        bgm_file=args.bgm_file,
        bgm_volume=args.bgm_volume,
        burn_in=args.no_soft_subs,
        generate_captions=args.generate_captions,
        language=args.language,
        sample_rate=args.sample_rate,
        keep_temp=args.keep_temp,
    )


if __name__ == "__main__":
    main()
