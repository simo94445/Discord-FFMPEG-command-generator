import subprocess
import shlex
import os

# Set this to your AV1 encoder: av1_nvenc (NVIDIA), av1_qsv (Intel), av1_amf (AMD)
AV1_ENCODER = "av1_nvenc"  # Change this if needed
#AV1_ENCODER = "av1_nvenc"     # NVIDIA 40xx
#AV1_ENCODER = "av1_qsv"       # Intel Arc
#AV1_ENCODER = "av1_amf"       # AMD RDNA3
#AV1_ENCODER = "libaom-av1"    # Slow af fallback

def probe_video(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration:stream=bit_rate",
        "-of", "default=noprint_wrappers=1:nokey=0",
        path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip().splitlines()

    duration = None
    audio_bitrate = 128_000  # fallback
    for line in output:
        if line.startswith("duration="):
            duration = float(line.split("=")[1])
    
    # Get audio bitrate
    cmd_audio = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=bit_rate",
        "-of", "default=noprint_wrappers=1:nokey=0",
        path
    ]
    result_audio = subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in result_audio.stdout.strip().splitlines():
        if line.startswith("bit_rate="):
            audio_bitrate = int(line.split("=")[1])
    
    return duration, audio_bitrate

def calculate_video_bitrate(duration, audio_bitrate, max_filesize_mb):
    total_bits = max_filesize_mb * 8 * 1024 * 1024
    video_bits = total_bits - (audio_bitrate * duration)
    video_bitrate = video_bits / duration
    fudge_factor = 0.95  # or 0.94 if you want to be extra safe
    video_bitrate = video_bitrate * fudge_factor
    return int(round(video_bitrate / 1000) * 1000)

def build_ffmpeg_command(input_file, output_file, video_bitrate, audio_bitrate):
    audio_bitrate = int(round(audio_bitrate / 1000) * 1000)

    cmd = f'ffmpeg -y -i "{input_file}" -c:v {AV1_ENCODER} -b:v {video_bitrate} -pix_fmt yuv420p -c:a aac -b:a {audio_bitrate} "{output_file}"'
    return cmd

def main():
    input_file = input("🎬 Enter input video filename (e.g. myclip.mp4): ").strip()
    if not os.path.exists(input_file):
        print(f"🚨 Input file '{input_file}' not found.")
        return

    default_output = os.path.splitext(input_file)[0] + "_av1.mp4"
    output_file = input(f"💾 Enter output filename [default: {default_output}]: ").strip()
    if not output_file:
        output_file = default_output

    try:
        max_size_mb = input("📦 Max file size in MB [default: 50]: ").strip()
        max_size_mb = int(max_size_mb) if max_size_mb else 50
    except ValueError:
        print("⚠️ Invalid size, using default of 50MB.")
        max_size_mb = 50

    duration, audio_bitrate = probe_video(input_file)
    video_bitrate = calculate_video_bitrate(duration, audio_bitrate, max_size_mb)

    print(f"\n⏱️ Duration: {duration:.2f}s")
    print(f"🔊 Audio bitrate: {audio_bitrate // 1000} kbps")
    print(f"🎯 Target AV1 video bitrate: {video_bitrate // 1000} kbps")

    ffmpeg_cmd = build_ffmpeg_command(input_file, output_file, video_bitrate, audio_bitrate)
    
    print("\n🔥 FFmpeg AV1 command (Discord-safe):")
    print(ffmpeg_cmd)

    run = input("🚀 Run command now? [Y/n]: ").strip().lower()
    if run in ["", "y", "yes"]:
        subprocess.run(shlex.split(ffmpeg_cmd), check=True)
        print("✅ Done.")
    else:
        print("❌ Skipped execution.")

if __name__ == "__main__":
    main()
