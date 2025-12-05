import math
import re
from collections import Counter
from typing import List, Dict


class TextProcessor:
    """Class for text preprocessing, tokenization, and stopword removal."""

    stopwords = set([
        'و', 'در', 'که', 'به', 'از', 'با', 'برای', 'آن', 'این', 'من', 'تو', 'او', 'اینکه', 'آنکه'
    ])

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Preprocess the input Persian text: lowercasing and removing non-Persian characters.
        
        Args:
            text (str): The input Persian text to be preprocessed.
        
        Returns:
            str: The cleaned, lowercase text with only Persian characters.
        """
        text = text.lower()
        text = re.sub(r'[^ء-ي\s]', '', text)  # Keeps only Persian characters and spaces
        return text

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenize the input text into a list of words.
        
        Args:
            text (str): The input preprocessed text.
        
        Returns:
            List[str]: A list of words (tokens).
        """
        return text.split()

    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        """
        Remove Persian stopwords from the list of tokens.
        
        Args:
            tokens (List[str]): The list of tokens.
        
        Returns:
            List[str]: The list of tokens with stopwords removed.
        """
        return [word for word in tokens if word not in TextProcessor.stopwords]


class TFIDFCalculator:
    """Class for calculating the Term Frequency-Inverse Document Frequency (TF-IDF) of a corpus."""

    @staticmethod
    def calculate_tf(corpus: List[List[str]]) -> List[Dict[str, int]]:
        """
        Calculate the Term Frequency (TF) for each document in the corpus.
        
        Args:
            corpus (List[List[str]]): A list of tokenized documents.
        
        Returns:
            List[Dict[str, int]]: A list of dictionaries containing the word frequencies for each document.
        """
        return [Counter(document) for document in corpus]

    @staticmethod
    def calculate_idf(corpus: List[List[str]]) -> Dict[str, float]:
        """
        Calculate the Inverse Document Frequency (IDF) for each word in the corpus.
        
        Args:
            corpus (List[List[str]]): A list of tokenized documents.
        
        Returns:
            Dict[str, float]: A dictionary containing the IDF values for each word.
        """
        total_documents = len(corpus)
        all_words = set(word for doc in corpus for word in doc)

        idf = {}
        for word in all_words:
            count = sum(1 for doc in corpus if word in doc)
            idf[word] = math.log(total_documents / (1 + count))  # Add 1 to avoid division by zero
        
        return idf

    @staticmethod
    def calculate_tf_idf(corpus: List[List[str]], idf: Dict[str, float]) -> List[Dict[str, float]]:
        """
        Calculate the TF-IDF for each document in the corpus.
        
        Args:
            corpus (List[List[str]]): A list of tokenized documents.
            idf (Dict[str, float]): A dictionary of IDF values for each word.
        
        Returns:
            List[Dict[str, float]]: A list of dictionaries containing the TF-IDF scores for each document.
        """
        tf = TFIDFCalculator.calculate_tf(corpus)

        tf_idf_scores = []
        for doc in tf:
            doc_scores = {}
            for word, freq in doc.items():
                tf_score = freq / len(doc)  # Term Frequency (TF)
                idf_score = idf.get(word, 0)  # Inverse Document Frequency (IDF)
                doc_scores[word] = tf_score * idf_score
            tf_idf_scores.append(doc_scores)
        
        return tf_idf_scores


class SimilarityCalculator:
    """Class for calculating similarity metrics between two documents."""

    @staticmethod
    def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculate the cosine similarity between two vectors (representing two documents).
        
        Args:
            vec1 (Dict[str, float]): The TF-IDF vector of the first document.
            vec2 (Dict[str, float]): The TF-IDF vector of the second document.
        
        Returns:
            float: The cosine similarity between the two vectors.
        """
        intersection = set(vec1) & set(vec2)
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1])
        sum2 = sum([vec2[x] ** 2 for x in vec2])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if denominator == 0:
            return 0.0
        else:
            return numerator / denominator if denominator != 0 else 0.0


class TextSimilarity:
    """Class to manage text preprocessing, TF-IDF calculation, and similarity measurement."""

    def __init__(self, text1: str, text2: str):
        """
        Initialize the TextSimilarity object with two texts.
        
        Args:
            text1 (str): The first Persian text.
            text2 (str): The second Persian text.
        """
        self.text1 = text1
        self.text2 = text2

    def process_and_calculate_similarity(self) -> float:
        """
        Process the texts (preprocessing, tokenization, stopword removal), 
        calculate their TF-IDF values, and compute the cosine similarity.
        
        Returns:
            float: The cosine similarity between the two texts.
        """
        # Preprocess and tokenize
        processed_text1 = TextProcessor.preprocess_text(self.text1)
        processed_text2 = TextProcessor.preprocess_text(self.text2)

        tokens1 = TextProcessor.tokenize(processed_text1)
        tokens2 = TextProcessor.tokenize(processed_text2)

        # Remove stopwords
        tokens1 = TextProcessor.remove_stopwords(tokens1)
        tokens2 = TextProcessor.remove_stopwords(tokens2)

        # Prepare the corpus for TF-IDF calculation
        corpus = [tokens1, tokens2]

        # Calculate TF-IDF
        idf_values = TFIDFCalculator.calculate_idf(corpus)
        tf_idf_scores = TFIDFCalculator.calculate_tf_idf(corpus, idf_values)

        # Calculate Cosine Similarity
        similarity = SimilarityCalculator.cosine_similarity(tf_idf_scores[0], tf_idf_scores[1])

        return similarity
