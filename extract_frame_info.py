import json

with open('ffprobe_output.json', 'r') as f:
    data = json.load(f)

for frame in data['frames']:
    print(f"key_frame: {frame['key_frame']}, pkt_dts_time: {frame['pkt_dts_time']}")
