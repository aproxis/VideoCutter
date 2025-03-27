# Template Files for VideoCutter

This directory contains template files required for the VideoCutter processing pipeline. These files are used for adding audio, transitions, and overlays to the final videos.

## Required Files

### Audio Templates

1. **soundtrack.mp3**
   - Background music for the slideshow
   - Recommended length: 2-3 minutes
   - Will be automatically trimmed to match video length

2. **transition.mp3**
   - Short sound effect for transitions between slides
   - Recommended length: 0.5-1 second
   - Used for individual transitions

3. **transition_long.mp3**
   - Extended version of transition sound
   - Used throughout the slideshow
   - Recommended length: 1-2 minutes

4. **voiceover_end.mp3**
   - Ending voiceover for the outro
   - Played during the outro section
   - Recommended length: 5-10 seconds

### Video Templates

1. **outro_vertical.mp4**
   - Outro video for vertical (9:16) format
   - Displayed at the end of the slideshow
   - Recommended length: 10-15 seconds
   - Resolution: 1080x1920

2. **outro_horizontal.mp4**
   - Outro video for horizontal (16:9) format
   - Displayed at the end of the slideshow
   - Recommended length: 10-15 seconds
   - Resolution: 1920x1080

3. **name_subscribe_like.mp4**
   - Subscription overlay for vertical (9:16) format
   - Should include a green screen background (chromakey color: #65db41)
   - Recommended resolution: 1080x1920

4. **name_subscribe_like_horizontal.mp4**
   - Subscription overlay for horizontal (16:9) format
   - Should include a green screen background (chromakey color: #65db41)
   - Recommended resolution: 1920x1080

## File Format Requirements

- **Audio Files**: MP3 format, stereo (2 channels)
- **Video Files**: MP4 format, H.264 codec
- **Vertical Videos**: 9:16 aspect ratio (e.g., 1080x1920)
- **Horizontal Videos**: 16:9 aspect ratio (e.g., 1920x1080)

## Customization

You can customize these template files to match your branding and style. Just make sure to:

1. Keep the same filenames
2. Maintain the required formats and codecs
3. Use the correct chromakey color (#65db41) for overlay videos
4. Ensure appropriate length for each template

## Troubleshooting

If you encounter issues with the templates:

1. Verify all required files are present
2. Check that file formats and codecs are correct
3. Ensure chromakey color is exactly #65db41
4. Confirm aspect ratios match the expected formats
