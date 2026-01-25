"""Split audio into segments based on transcript.json."""
from pathlib import Path
import sys

from src.cli import parse_split_args
from src.splitter import AudioSplitter
from src.json_loader import load_transcript_json, segments_to_whisper_format


def main():
    """Main splitting pipeline."""
    print("=" * 60)
    print("Audio Splitting Tool")
    print("=" * 60)

    # Parse arguments
    try:
        args = parse_split_args()
    except SystemExit:
        return 1

    output_dir = Path(args.output_dir)

    print(f"\nOutput directory: {output_dir}")

    try:
        # Step 1: Load JSON
        print("\n" + "-" * 40)
        print("Loading transcript.json...")
        print("-" * 40)

        data = load_transcript_json(str(output_dir / "transcript.json"))
        source_audio = Path(data["source_file"])

        print(f"Source audio: {source_audio}")
        print(f"Segments: {len(data['segments'])}")

        # Verify source audio exists
        if not source_audio.exists():
            print(f"\n[ERROR] Source audio file not found: {source_audio}")
            print("Please ensure the audio file exists at the path specified in transcript.json")
            return 1

        segments = segments_to_whisper_format(data["segments"])

        # Step 2: Split audio
        print("\n" + "-" * 40)
        print("Splitting audio...")
        print("-" * 40)

        splitter = AudioSplitter(
            audio_path=str(source_audio),
            output_dir=str(output_dir),
            margin_before=args.margin_before,
            margin_after=args.margin_after,
            max_filename_length=args.max_filename_length,
        )

        metadata = splitter.split_and_save(segments)
        splitter.save_metadata(metadata)

        # Summary
        print("\n" + "=" * 60)
        print("Splitting Complete!")
        print("=" * 60)
        print(f"Total segments: {len(metadata)}")
        print(f"Output directory: {output_dir.absolute()}")

        # Show sample outputs
        print("\nOutput files:")
        for item in metadata[:5]:
            print(f"  - {item['filename']}")
        if len(metadata) > 5:
            print(f"  ... and {len(metadata) - 5} more files")

        return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
