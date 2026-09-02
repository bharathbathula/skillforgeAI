import re
import unicodedata
from typing import List, Set, Dict

class TechnicalTokenizer:
    """
    Tokenizer tailored for ATS and technical documents.
    Preserves symbols in language and tech names like C++, C#, .NET, Node.js, React.js,
    CI/CD, REST APIs, TCP/IP, and normalizes aliases.
    """

    # Skill and tool alias mappings (lowercase target)
    TECH_ALIASES: Dict[str, str] = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "golang": "go",
        "reactjs": "react",
        "react.js": "react",
        "nodejs": "node.js",
        "node": "node.js",
        "vuejs": "vue",
        "vue.js": "vue",
        "nextjs": "next.js",
        "nuxtjs": "nuxt.js",
        "postgres": "postgresql",
        "psql": "postgresql",
        "mongo": "mongodb",
        "k8s": "kubernetes",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
        "azure": "microsoft azure",
        "rest": "rest api",
        "restful": "rest api",
        "restful api": "rest api",
        "restful apis": "rest api",
        "ci/cd": "ci/cd pipeline",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "genai": "generative ai",
        "llm": "large language models",
        "llms": "large language models",
        "tf": "tensorflow",
        "scikit": "scikit-learn",
        "sklearn": "scikit-learn",
        "sqla": "sqlalchemy"
    }

    # Standard English stopwords (excluding technical tokens like 'c', 'r', 'go', 'net', 'it')
    STOPWORDS: Set[str] = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
        "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
        "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
        "if", "in", "into", "is", "its", "itself", "me", "more", "most", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
        "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
        "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
        "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself"
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Normalize unicode, whitespace, and bullets without destroying technical terms."""
        if not text:
            return ""

        # Normalize unicode (NFKD)
        text = unicodedata.normalize('NFKD', text)

        # Standardize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Replace bullet points with standard newlines/hyphens
        for b in ['\u2022', '\u2023', '\u25e6', '\u2043', '\u2219', '\u25aa', '\u25ab', '\u25cf', '\uf0b7', '\ufffd']:
            text = text.replace(b, '\n- ')

        # Standardize quotes and dashes
        text = (text.replace('\u2013', '-').replace('\u2014', '-')
                    .replace('\u2018', "'").replace('\u2019', "'")
                    .replace('\u201c', '"').replace('\u201d', '"'))

        return text.strip()

    @classmethod
    def tokenize_preserve_tech(cls, text: str) -> List[str]:
        """
        Tokenizes text into a list of words/phrases while preserving terms like
        C++, C#, .NET, Node.js, Next.js, CI/CD, REST-API, etc.
        """
        cleaned = cls.clean_text(text)
        if not cleaned:
            return []

        # Regex pattern matching special tech tokens first, then words with dots/dashes, then words
        pattern = r'''(?x)
            (?:[cC]\+\+)                   # C++
            |(?:[cC]\#)                    # C#
            |(?:\.NET|\.net)               # .NET
            |(?:[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)+) # Node.js, Vue.js, v1.5, etc.
            |(?:[a-zA-Z0-9]+(?:[\/-][a-zA-Z0-9]+)+) # CI/CD, REST-API, TCP/IP, Py-Torch
            |(?:\b[a-zA-Z0-9_]+\b)         # Standard words and identifiers
        '''

        tokens = re.findall(pattern, cleaned)
        return tokens

    @classmethod
    def normalize_skill(cls, skill_name: str) -> str:
        """Normalize a skill name using alias mappings and lowercase stripping."""
        if not skill_name:
            return ""
        s = skill_name.strip().lower()
        return cls.TECH_ALIASES.get(s, s)

    @classmethod
    def extract_keywords_filtered(cls, text: str) -> List[str]:
        """Extract unique lowercased non-stopword technical and domain keywords."""
        tokens = cls.tokenize_preserve_tech(text)
        keywords = []
        seen = set()

        for t in tokens:
            low = t.lower()
            if len(low) > 1 and low not in cls.STOPWORDS and low not in seen:
                seen.add(low)
                keywords.append(t)

        return keywords
