from pydub import AudioSegment

# Duration in milliseconds
transition_duration = 500  # 0.5 seconds
total_duration = 10 * 60 * 1000  # 10 minutes in milliseconds

# Load the transition sound as an AudioSegment
transition_sound = AudioSegment.from_file("TEMPLATE/transition_500ms.mp3")

# Create the initial audio with silence and the first transition
audio = AudioSegment.silent(duration=4500)  # 4.5 seconds of silence
audio += transition_sound  # Add the first transition sound

# Calculate the number of transitions to add
num_transitions = (total_duration - 4500) // 5000  # Add a transition every 5 seconds

# Add transitions every 5 seconds after the first one
for i in range(num_transitions):
    audio += AudioSegment.silent(duration=4500)  # 5 seconds of silence
    audio += transition_sound  # Add the transition sound

# Export the final audio as an MP3 file
output_path = "TEMPLATE/transition_long.mp3"
audio.export(output_path, format="mp3")

print(f"Audio file created: {output_path}")
