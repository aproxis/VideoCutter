import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Get the transcript
srt = YouTubeTranscriptApi.get_transcript("KFA4B1pTvaA")

# Initialize a TextFormatter
formatter = TextFormatter()

# Format the transcript
text_formatted = formatter.format_transcript(srt)

# Replace single line breaks with spaces
text_formatted = re.sub(r'\n(?!\n)', ' ', text_formatted)

# Write the formatted transcript to a file
with open('videos.txt', 'w', encoding='utf-8') as text_file:
    text_file.write(text_formatted)

# Print the result
print(srt)
print(text_formatted)
