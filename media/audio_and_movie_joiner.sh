#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
START_EPOCH="$(date +%s)"

VIDEO_FILE=""
AUDIO_FILE=""
OUTPUT_FILE=""
MODE="copy"
KEEP_ORIGINAL_AUDIO="no"
OVERWRITE="no"

usage() {
  cat <<'EOF'
audio_and_movie_joiner.sh - combine one video with one external audio track

Usage:
  ./audio_and_movie_joiner.sh --video VIDEO --audio AUDIO [--output OUTPUT] [options]
  ./audio_and_movie_joiner.sh --help

Required:
  -v, --video FILE     Input video file.
  -a, --audio FILE     Input audio file to place under the video.

Options:
  -o, --output FILE    Output file.
                      Default:
                        joined.mkv for --mode copy or --mode lossless
                        linkedin-final.mp4 for --mode linkedin
  -m, --mode MODE      Output mode:
                        copy      Copy video and audio streams without re-encoding.
                                  Best quality, no generation loss. Uses MKV by default.
                        linkedin  Render LinkedIn-friendly MP4: H.264 video + AAC audio,
                                  30 fps, and 48 kHz audio.
                                  This is compatible, but AAC/H.264 are lossy codecs.
                        lossless  Re-encode to mathematically lossless FFV1 + FLAC in MKV.
                                  Very large file. Useful as an editing master.
                      Default: copy
      --keep-original-audio
                      Keep the video's existing audio tracks too.
                      By default, only the external audio is used.
  -y, --overwrite      Overwrite output file if it already exists.
  -h, --help           Show this help.

Behavior:
  - The video and audio start at the same time.
  - The full video is kept.
  - The full external audio track is kept.
  - No -shortest flag is used. If the video is longer than the audio, playback continues
    to the end of the video and the missing audio tail is silent in normal players.
  - In copy mode, FFmpeg only remuxes streams. If the chosen output container cannot hold
    the input codecs, use .mkv or choose --mode linkedin.

Examples:
  ./audio_and_movie_joiner.sh \
    --video myLastFmPlayer_v0.0.127_recording.webm \
    --audio post_audio.ac3 \
    --output joined.mkv

  ./audio_and_movie_joiner.sh \
    --video myLastFmPlayer_v0.0.127_recording.webm \
    --audio post_audio.ac3 \
    --mode linkedin \
    --output linkedin-final.mp4

Suggested Manjaro workflow:
  1. Record narration with Audacity:
       sudo pacman -S audacity ffmpeg
     Export WAV/FLAC for best intermediate quality.

  2. Combine with this script:
       ./audio_and_movie_joiner.sh --video video.webm --audio narration.wav --output master.mkv

  3. For LinkedIn upload, render a compatible MP4:
       ./audio_and_movie_joiner.sh --video video.webm --audio narration.wav --mode linkedin --output linkedin-final.mp4

  GUI alternative:
    sudo pacman -S kdenlive
    Use Kdenlive when you need trimming, fades, volume balancing, or original sound under voice.
EOF
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  printf 'ERROR: %s\n\n' "$*" >&2
  usage >&2
  exit 1
}

finish() {
  local exit_code=$?
  local end_epoch elapsed
  end_epoch="$(date +%s)"
  elapsed=$((end_epoch - START_EPOCH))
  if [[ $exit_code -eq 0 ]]; then
    log "Done. Total elapsed time: $(format_seconds "$elapsed")."
  else
    log "Failed after $(format_seconds "$elapsed")."
  fi
  exit "$exit_code"
}

format_seconds() {
  local total=$1
  local hours minutes seconds
  hours=$((total / 3600))
  minutes=$(((total % 3600) / 60))
  seconds=$((total % 60))
  printf '%02d:%02d:%02d' "$hours" "$minutes" "$seconds"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    die "Required command not found: $1"
  fi
}

quote_cmd() {
  printf ' %q' "$@"
  printf '\n'
}

duration_of() {
  local file=$1
  ffprobe \
    -v error \
    -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 \
    "$file" 2>/dev/null || true
}

human_duration() {
  local raw=$1
  if [[ -z "$raw" || "$raw" == "N/A" ]]; then
    printf 'unknown'
    return
  fi
  awk -v seconds="$raw" 'BEGIN {
    total = int(seconds + 0.5);
    printf "%02d:%02d:%02d", int(total / 3600), int((total % 3600) / 60), total % 60;
  }'
}

parse_args() {
  if [[ $# -eq 0 ]]; then
    usage
    exit 0
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -v|--video)
        [[ $# -ge 2 ]] || die "Missing value for $1"
        VIDEO_FILE=$2
        shift 2
        ;;
      -a|--audio)
        [[ $# -ge 2 ]] || die "Missing value for $1"
        AUDIO_FILE=$2
        shift 2
        ;;
      -o|--output)
        [[ $# -ge 2 ]] || die "Missing value for $1"
        OUTPUT_FILE=$2
        shift 2
        ;;
      -m|--mode)
        [[ $# -ge 2 ]] || die "Missing value for $1"
        MODE=$2
        shift 2
        ;;
      --keep-original-audio)
        KEEP_ORIGINAL_AUDIO="yes"
        shift
        ;;
      -y|--overwrite)
        OVERWRITE="yes"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument: $1"
        ;;
    esac
  done
}

validate_inputs() {
  require_command ffmpeg
  require_command ffprobe
  require_command awk

  [[ -n "$VIDEO_FILE" ]] || die "Missing required --video FILE"
  [[ -n "$AUDIO_FILE" ]] || die "Missing required --audio FILE"
  [[ -f "$VIDEO_FILE" ]] || die "Video file does not exist: $VIDEO_FILE"
  [[ -f "$AUDIO_FILE" ]] || die "Audio file does not exist: $AUDIO_FILE"

  case "$MODE" in
    copy|linkedin|lossless) ;;
    *) die "Unsupported mode: $MODE" ;;
  esac

  if [[ -z "$OUTPUT_FILE" ]]; then
    case "$MODE" in
      linkedin) OUTPUT_FILE="linkedin-final.mp4" ;;
      *) OUTPUT_FILE="joined.mkv" ;;
    esac
  fi

  if [[ -e "$OUTPUT_FILE" && "$OVERWRITE" != "yes" ]]; then
    die "Output already exists: $OUTPUT_FILE. Use --overwrite to replace it."
  fi
}

build_ffmpeg_command() {
  local overwrite_flag="-n"
  [[ "$OVERWRITE" == "yes" ]] && overwrite_flag="-y"

  FFMPEG_CMD=(ffmpeg "$overwrite_flag" -hide_banner -stats -i "$VIDEO_FILE" -i "$AUDIO_FILE")

  case "$MODE" in
    copy)
      FFMPEG_CMD+=(-map 0:v:0 -map 1:a:0)
      if [[ "$KEEP_ORIGINAL_AUDIO" == "yes" ]]; then
        FFMPEG_CMD+=(-map '0:a?')
      fi
      FFMPEG_CMD+=(-map_metadata 0 -c copy "$OUTPUT_FILE")
      ;;
    linkedin)
      FFMPEG_CMD+=(-map 0:v:0 -map 1:a:0)
      if [[ "$KEEP_ORIGINAL_AUDIO" == "yes" ]]; then
        log "Note: --keep-original-audio is ignored in linkedin mode to keep one predictable upload audio track."
      fi
      FFMPEG_CMD+=(
        -map_metadata 0
        -c:v libx264
        -preset slow
        -crf 18
        -filter:v fps=30
        -pix_fmt yuv420p
        -movflags +faststart
        -c:a aac
        -b:a 192k
        -ar 48000
        "$OUTPUT_FILE"
      )
      ;;
    lossless)
      FFMPEG_CMD+=(-map 0:v:0 -map 1:a:0)
      if [[ "$KEEP_ORIGINAL_AUDIO" == "yes" ]]; then
        FFMPEG_CMD+=(-map '0:a?')
      fi
      FFMPEG_CMD+=(
        -map_metadata 0
        -c:v ffv1
        -level 3
        -g 1
        -c:a flac
        "$OUTPUT_FILE"
      )
      ;;
  esac
}

main() {
  trap finish EXIT
  parse_args "$@"
  validate_inputs

  local video_duration audio_duration
  video_duration="$(duration_of "$VIDEO_FILE")"
  audio_duration="$(duration_of "$AUDIO_FILE")"

  log "Starting audio/video join."
  log "Mode: $MODE"
  log "Video: $VIDEO_FILE ($(human_duration "$video_duration"))"
  log "Audio: $AUDIO_FILE ($(human_duration "$audio_duration"))"
  log "Output: $OUTPUT_FILE"
  log "Original video audio: $KEEP_ORIGINAL_AUDIO"
  log "Keeping complete streams; not using -shortest."

  build_ffmpeg_command

  log "Running FFmpeg command:"
  quote_cmd "${FFMPEG_CMD[@]}"

  "${FFMPEG_CMD[@]}"

  log "Created output file:"
  ls -lh "$OUTPUT_FILE"
}

main "$@"
