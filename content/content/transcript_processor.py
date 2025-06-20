import openai
import os
import csv
import re
import nltk
import logging
from datetime import datetime
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from content.config import Config # Import Config from content.config

# ---- Логирование ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Цены моделей OpenAI ----
PRICING = {
    "gpt-4o": {"prompt": 0.0000025, "completion": 0.00001},
    "gpt-4o-mini": {"prompt": 0.00000015, "completion": 0.0000006},
    "gpt-4.1": {"prompt": 0.000002, "completion": 0.000008},
    "gpt-4.1-mini": {"prompt": 0.0000004, "completion": 0.0000016},
    "gpt-4.1-nano": {"prompt": 0.0000001, "completion": 0.0000004},
    "gpt-3.5-turbo": {"prompt": 0.0000005, "completion": 0.0000015}
}

# ---- Основной класс ----
class TranscriptProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key) # Initialize OpenAI client
        self._ensure_nltk_data()
        self._openai_auto_approve = False # Flag for "yes to all"
        logger.info("TranscriptProcessor initialized")

    def _ensure_nltk_data(self):
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

    def calculate_cost(self, prompt_tokens, completion_tokens):
        pricing = PRICING.get(self.config.ai_model.lower(), {"prompt": 0, "completion": 0})
        return prompt_tokens * pricing["prompt"] + completion_tokens * pricing["completion"]

    def log_usage_to_csv(self, model, usage, cost):
        log_file = self.config.log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode="a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["timestamp", "model", "prompt_tokens", "completion_tokens", "total_tokens", "cost_usd"])
            writer.writerow([
                datetime.utcnow().isoformat(),
                model,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
                f"{cost:.6f}"
            ])

    def rewrite_transcript(self, transcript: str) -> str:
        # Check for user approval for OpenAI rewriting
        if not self._openai_auto_approve:
            user_input = input("Rewrite transcript using OpenAI? (y/n/a): ").lower()
            if user_input == 'a':
                self._openai_auto_approve = True
            elif user_input != 'y':
                logger.info("Skipping OpenAI transcript rewriting as per user request.")
                return transcript # Return original transcript if skipped

        try:
            messages = [
                {"role": "system", "content": self.config.rewrite_prompt},
                {"role": "user", "content": f"Please rewrite this transcript:\n\n{transcript}"}
            ]
            response = self.client.chat.completions.create( # Use client-based API call
                model=self.config.ai_model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=0.7
            )
            rewritten = response.choices[0].message.content
            usage = response.usage
            cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)

            logger.info(f"OpenAI response received. Tokens: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}, cost=${cost:.6f}")
            # Assuming log_to_csv is a boolean in the centralized Config
            if hasattr(self.config, 'log_to_csv') and self.config.log_to_csv:
                self.log_usage_to_csv(self.config.ai_model, usage, cost)
            elif not hasattr(self.config, 'log_to_csv'):
                logger.warning("Config does not have 'log_to_csv' attribute. Defaulting to not logging.")


            return rewritten
        except Exception as e:
            logger.error(f"AI rewriting failed: {e}", exc_info=True)
            return transcript

    def extract_keywords(self, text: str, num_keywords: int = 10, language: str = "english"):
        logger.info(f"Extracting {num_keywords} keywords...")
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = word_tokenize(text)
        stop_words = set(stopwords.words(language))
        filtered = [w for w in words if w not in stop_words and len(w) > 3]
        word_freq = Counter(filtered)
        return [word for word, _ in word_freq.most_common(num_keywords)]

# ---- Пример использования ----
if __name__ == "__main__":
    cfg = Config() # Use the imported Config
    processor = TranscriptProcessor(cfg)

    raw = "today we discuss the future of AI. it's changing everything. people are worried. but others are excited."
    rewritten = processor.rewrite_transcript(raw)
    keywords = processor.extract_keywords(rewritten)

    print("Rewritten transcript:\n", rewritten)
    print("\nKeywords:", keywords)
