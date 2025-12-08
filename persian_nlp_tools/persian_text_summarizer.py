from parsivar import Normalizer, Tokenizer
import re

class TextProcessor:
    """Class for normalizing and preprocessing Persian text."""

    @staticmethod
    def normalize_persian_numbers(text: str) -> str:
        """
        Normalize Persian digits to Arabic numerals.
        
        Args:
            text (str): The Persian text with potential Persian digits.
        
        Returns:
            str: The text with Persian digits normalized to Arabic numerals.
        """
        persian_numbers = {
            "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"
        }
        for persian, arabic in persian_numbers.items():
            text = text.replace(persian, arabic)
        return text

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Preprocess the text by normalizing Persian numbers and removing unwanted spaces.
        
        Args:
            text (str): The original Persian text.
        
        Returns:
            str: The preprocessed text.
        """
        # Normalize Persian numbers
        text = TextProcessor.normalize_persian_numbers(text)
        
        # Handle number with periods like "1.", "2." by replacing them with a space after the number
        text = re.sub(r'(\d+)\.(\s)', r'\1\2', text)

        # Remove extra spaces
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text


class TextSummarizer:
    """Class for summarizing text using Parsivar tokenizer and sentence-based summarization."""

    def __init__(self, text: str, ratio: float, sentence_limit: int = 5):
        """
        Initialize the TextSummarizer with text and parameters for summarization.
        
        Args:
            text (str): The input Persian text to summarize.
            ratio (float): The ratio of sentences to include in the summary (e.g., 0.3 for 30%).
            sentence_limit (int): The maximum number of sentences in the summary (default is 5).
        """
        self.text = text
        self.ratio = ratio
        self.sentence_limit = sentence_limit

    def generate_summary(self) -> str:
        """
        Process the text, tokenize into sentences, and generate a summary based on the given ratio and sentence limit.
        
        Returns:
            str: The generated summary.
        """
        # Preprocess the text first
        preprocessed_text = TextProcessor.preprocess_text(self.text)

        # Initialize Parsivar Normalizer
        normalizer = Normalizer()
        normalized_text = normalizer.normalize(preprocessed_text)

        # Tokenize the text into sentences
        tokenizer = Tokenizer()
        sentences = tokenizer.tokenize_sentences(normalized_text)
        
        # Filter out any empty sentences
        sentences = [sentence for sentence in sentences if sentence.strip()]

        # Calculate the number of sentences to include in the summary
        num_sentences = len(sentences)
        num_summary_sentences = int(num_sentences * self.ratio)
        
        # Ensure the summary doesn't exceed the sentence limit
        summary_sentences = sentences[:min(num_summary_sentences, self.sentence_limit)]

        # Join the summary sentences
        summary = "\n".join(summary_sentences)

        return summary


class TextSummarizationPipeline:
    """Class to manage the full text summarization process, from preprocessing to generating and printing the result."""

    def __init__(self, text: str, ratio: float, sentence_limit: int = 5):
        """
        Initialize the summarization pipeline.
        
        Args:
            text (str): The input text for summarization.
            ratio (float): The ratio of sentences to include in the summary.
            sentence_limit (int): The maximum number of sentences in the summary (default is 5).
        """
        self.text = text
        self.ratio = ratio
        self.sentence_limit = sentence_limit

    def process_and_summarize(self) -> None:
        """
        Run the entire summarization process: preprocess and summarize the text.
        
        Returns:
            None
        """
        # Initialize the summarizer
        summarizer = TextSummarizer(self.text, self.ratio, self.sentence_limit)

        # Generate the summary
        summary = summarizer.generate_summary()

        # Print the summary
        return summary
