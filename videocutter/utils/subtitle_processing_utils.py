import re
import logging
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def format_timestamp_ass(seconds: Optional[float]) -> str:
    """Format timestamp for ASS format (centiseconds)"""
    if seconds is None:
        return "0:00:00.00"
    
    seconds = max(0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centisecs:02}"

def split_subtitle_text_ass(text: str, max_chars_per_line: int, max_lines_per_subtitle: int) -> str:
    """
    Splits text into lines for ASS format, respecting max characters per line and max lines per subtitle.
    Uses \\N for line breaks.
    """
    logger.debug(f"Entering split_subtitle_text_ass. Input text (first 50 chars): '{text[:50]}'")
    words = text.split()
    if not words:
        return text
    
    lines = []
    current_line_words = []
    current_line_char_count = 0
    
    for word in words:
        # Calculate length if word is added to current line (plus one for space)
        # If current_line_words is empty, no leading space needed
        potential_new_length = current_line_char_count + len(word) + (1 if current_line_words else 0)
        
        if potential_new_length > max_chars_per_line and current_line_words:
            # Current word exceeds max_chars_per_line, so finalize current line
            lines.append(' '.join(current_line_words))
            
            # Check if we've reached the maximum number of lines
            if len(lines) >= max_lines_per_subtitle:
                break # Stop adding new lines
            
            # Start a new line with the current word
            current_line_words = [word]
            current_line_char_count = len(word)
        else:
            # Add word to current line
            current_line_words.append(word)
            current_line_char_count = potential_new_length if current_line_words else len(word) # Update char count

    # Add any remaining words as the last line, if max_lines_per_subtitle not exceeded
    if current_line_words and len(lines) < max_lines_per_subtitle:
        lines.append(' '.join(current_line_words))
    elif current_line_words and len(lines) == max_lines_per_subtitle:
        # If max lines reached, but there are remaining words, append to the last line
        # This prevents losing words if they don't fit on a new line
        if lines:
            lines[-1] += ' ' + ' '.join(current_line_words)
        else: # Should not happen if current_line_words is true
            lines.append(' '.join(current_line_words))
    
    split_text = '\\N'.join(lines)
    logger.debug(f"Exiting split_subtitle_text_ass. Returned text (first 50 chars): '{split_text[:50]}'")
    return split_text


def split_at_sentence_boundaries(word_data: List[Dict]) -> List[Dict]:
    """
    Splits a list of word data (with 'word', 'start', 'end') into sentence-level cues.
    It identifies sentence boundaries based on punctuation within the words themselves.
    """
    logger.debug(f"Entering split_at_sentence_boundaries. Input word_data contains {len(word_data)} words.")
    if not word_data:
        return []

    sentence_cues = []
    current_sentence_words = []
    current_sentence_start_time = None
    
    for i, word_info in enumerate(word_data):
        word = word_info.get('word', '').strip()
        start_time = word_info.get('start')
        end_time = word_info.get('end')

        if not word:
            continue

        if current_sentence_start_time is None:
            current_sentence_start_time = start_time

        current_sentence_words.append(word)

        # Check for sentence-ending punctuation at the end of the word
        # This regex handles cases like "word." "word!" "word?" "word." (with quotes)
        # and ensures it's at the end of the word, not in the middle.
        if re.search(r'[.!?]["\']?$', word):
            # Found a sentence end
            sentence_text = " ".join(current_sentence_words)
            sentence_cues.append({
                'text': sentence_text,
                'start': current_sentence_start_time,
                'end': end_time # End time of the last word in the sentence
            })
            logger.debug(f"Extracted sentence: '{sentence_text}', Start: {current_sentence_start_time:.2f}s, End: {end_time:.2f}s")
            # Reset for the next sentence
            current_sentence_words = []
            current_sentence_start_time = None
        elif i == len(word_data) - 1: # If it's the last word and no punctuation, treat as end of sentence
            sentence_text = " ".join(current_sentence_words)
            sentence_cues.append({
                'text': sentence_text,
                'start': current_sentence_start_time,
                'end': end_time
            })
            logger.debug(f"Extracted sentence: '{sentence_text}', Start: {current_sentence_start_time:.2f}s, End: {end_time:.2f}s")

    logger.debug(f"Exiting split_at_sentence_boundaries. Generated {len(sentence_cues)} sentence cues.")
    return sentence_cues

def merge_short_subtitles(cues: List[Dict], min_duration: float, max_duration: float, min_gap: float) -> List[Dict]:
    """Merge short subtitles with improved logic"""
    logger.debug(f"Entering merge_short_subtitles. Input cues: {len(cues)}.")
    if not cues:
        return cues
    
    merged_cues = []
    current_cue = None
    
    for i, cue in enumerate(cues):
        duration = cue['end'] - cue['start']
        
        if current_cue is None:
            current_cue = cue.copy()
        else:
            # Check if should merge based on duration and gap
            gap = cue['start'] - current_cue['end']
            combined_duration = cue['end'] - current_cue['start']
            
            should_merge = (
                duration < min_duration or
                (gap < min_gap and combined_duration < max_duration)
            )
            
            if should_merge:
                current_cue['text'] += ' ' + cue['text']
                current_cue['end'] = cue['end']
                logger.debug(f"Merging cue '{cue['text'][:20]}...' (duration: {duration:.2f}s, gap: {gap:.2f}s) with current cue. Combined duration: {combined_duration:.2f}s")
            else:
                merged_cues.append(current_cue)
                current_cue = cue.copy()
                logger.debug(f"Starting new cue with '{cue['text'][:20]}...'.")
    
    if current_cue:
        merged_cues.append(current_cue)
    
    logger.debug(f"Exiting merge_short_subtitles. Generated {len(merged_cues)} merged cues.")
    return merged_cues

def _similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def _find_best_match_segment(transcribed_word: str, original_words: List[str], start_idx: int, search_window: int = 5) -> Tuple[int, float]:
    """
    Find the best matching word in the original text within a search window.
    Returns the index of the best match and its similarity score.
    """
    best_match_idx = start_idx
    max_similarity = -1.0

    # Search forward within a limited window
    for i in range(start_idx, min(len(original_words), start_idx + search_window)):
        sim = _similarity(transcribed_word, original_words[i])
        if sim > max_similarity:
            max_similarity = sim
            best_match_idx = i
    
    return best_match_idx, max_similarity
