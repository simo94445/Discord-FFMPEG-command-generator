```python
git clone https://github.com/simo94445/Discord-FFMPEG-command-generator.git
cd Discord-FFMPEG-command-generator
python generate_ffmpeg_command.py
```
Example output:
```
PS W:\OBSReplays> python .\generate_ffmpeg_command.py
🎬 Enter input video filename (e.g. myclip.mp4): 4-4greed.mp4
💾 Enter output filename [default: 4-4greed_av1.mp4]:
📦 Max file size in MB [default: 50]:

⏱️ Duration: 96.77s
🔊 Audio bitrate: 161 kbps
🎯 Target AV1 video bitrate: 3964 kbps

🔥 FFmpeg AV1 command (Discord-safe):
ffmpeg -y -i "4-4greed.mp4" -c:v av1_nvenc -b:v 3964000 -pix_fmt yuv420p -c:a aac -b:a 161000 "4-4greed_av1.mp4"
🚀 Run command now? [Y/n]: 
```

The script uses hardware encoding for nVidia 4xxx series GPUs, you can change the encoder at:

```python
AV1_ENCODER = "av1_nvenc"  # Change this if needed
#AV1_ENCODER = "av1_nvenc"     # NVIDIA 40xx
#AV1_ENCODER = "av1_qsv"       # Intel Arc
#AV1_ENCODER = "av1_amf"       # AMD RDNA3
#AV1_ENCODER = "libaom-av1"    # Slow af fallback
```
To find your encoder (if available), do:

```
ffmpeg -hide_banner -encoders | findstr av1
```

That should output something like:

```
 V....D libaom-av1           libaom AV1 (codec av1)
 V....D av1_nvenc            NVIDIA NVENC av1 encoder (codec av1)
 V..... av1_qsv              AV1 (Intel Quick Sync Video acceleration) (codec av1)
 V....D av1_amf              AMD AMF AV1 encoder (codec av1)
 V....D av1_vaapi            AV1 (VAAPI) (codec av1)
 A....D wmav1                Windows Media Audio 1
```

Those are your supported encoders. 
