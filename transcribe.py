"""Transcribe audio file using Whisper."""
from pathlib import Path
import sys

from src.cli import parse_transcribe_args
from src.transcribe import Transcriber
from src.splitter import AudioSplitter


def main():
    """Main transcription pipeline."""
    print("=" * 60)
    print("Audio Transcription Tool")
    print("=" * 60)

    # Parse arguments
    try:
        args = parse_transcribe_args()
    except SystemExit:
        return 1

    input_file = Path(args.input_file)

    # Generate default output directory
    if args.output_dir is None:
        output_dir = str(input_file.parent / f"{input_file.stem}_generated")
    else:
        output_dir = args.output_dir

    print(f"\nInput file: {input_file}")
    print(f"Model: {args.model}")
    print(f"Output directory: {output_dir}")

    try:
        # Step 1: Initialize transcriber
        print("\n" + "-" * 40)
        print("Loading Whisper model...")
        print("-" * 40)

        transcriber = Transcriber(
            model_name=args.model,
            language=args.language,
            device=args.device
        )

        # Display device info
        if transcriber.gpu_name:
            print(f"Using GPU: {transcriber.gpu_name}")
        else:
            print("Using CPU")
        print(f"Model: {transcriber.model_name} on {transcriber.device}")

        # Step 2: Transcribe
        print("\n" + "-" * 40)
        print(f"Transcribing: {input_file.name}")
        print("-" * 40)

        result = transcriber.transcribe(str(input_file))
        segments = transcriber.get_segments(result)

        print(f"Found {len(segments)} speech segments")

        if not segments:
            print("\nNo speech segments detected. Exiting.")
            return 0

        # Step 3: Generate metadata
        print("\n" + "-" * 40)
        print("Generating metadata...")
        print("-" * 40)

        splitter = AudioSplitter(
            audio_path=str(input_file),
            output_dir=output_dir,
        )

        metadata = splitter.generate_metadata_only(segments)
        splitter.save_metadata(metadata, unexported=True)

        # Summary
        print("\n" + "=" * 60)
        print("Transcription Complete!")
        print("=" * 60)
        print(f"Total segments: {len(metadata)}")
        print(f"Output directory: {Path(output_dir).absolute()}")
        print(f"Metadata file: transcript_unexported.json")
        print("\nNext step:")
        print(f"  uv run python edit.py {output_dir}")

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
