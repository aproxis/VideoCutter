import logging
from deepmultilingualpunctuation import PunctuationModel

logger = logging.getLogger(__name__)
logger.debug("punctuation_utils.py imported.")

class PunctuationFixer:
    """
    A utility class to handle punctuation restoration using deepmultilingualpunctuation.
    """
    def __init__(self):
        logger.debug("PunctuationFixer instance created.")
        self.punct_model = None
        self._load_punctuation_model()

    def _load_punctuation_model(self):
        """
        Load punctuation model with error handling.
        """
        try:
            self.punct_model = PunctuationModel()
            logger.info("Punctuation model loaded successfully.")
            logger.debug("Punctuation model loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load punctuation model: {e}. Punctuation fix will be unavailable.")
            logger.error(f"Failed to load punctuation model: {e}. Punctuation fix will be unavailable.")
            self.punct_model = None

    def restore_punctuation(self, text: str) -> str:
        """
        Restores punctuation in the given text if the model is loaded.
        Returns the original text if the model is not loaded or an error occurs.
        """
        logger.debug(f"Entering restore_punctuation. Input text (first 50 chars): '{text[:50]}'")
        if self.punct_model:
            try:
                restored_text = self.punct_model.restore_punctuation(text)
                logger.debug(f"Exiting restore_punctuation. Returned text (first 50 chars): '{restored_text[:50]}'")
                return restored_text
            except Exception as e:
                logger.warning(f"Punctuation restoration failed for text: '{text[:50]}...'. Error: {e}. Returning original text.")
                logger.error(f"Punctuation restoration failed for text: '{text[:50]}...'. Error: {e}. Returning original text.")
                return text
        else:
            logger.warning("Punctuation model not loaded. Skipping punctuation restoration.")
            return text

# Global instance to avoid reloading the model multiple times
punctuation_fixer_instance = PunctuationFixer()

def apply_punctuation_fix(text: str) -> str:
    """
    Convenience function to apply punctuation fix using the global instance.
    """
    return punctuation_fixer_instance.restore_punctuation(text)
