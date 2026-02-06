import spacy
import re
from typing import Dict, List

class NLPEngine:
    """
    Handles basic NLP tasks like NER, Classification, and Segmentation.
    """
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # Fallback or download command could be triggered here
            import os
            os.system(f"python -m spacy download {model}")
            self.nlp = spacy.load(model)

    def classify_contract(self, text: str) -> str:
        """
        Heuristic-based classification of contract type.
        Can be improved with LLM later.
        """
        text_lower = text.lower()
        if "employment" in text_lower or "employee" in text_lower:
            return "Employment Agreement"
        elif "lease" in text_lower or "tenant" in text_lower:
            return "Lease Agreement"
        elif "vendor" in text_lower or "supplier" in text_lower:
            return "Vendor Contract"
        elif "partnership" in text_lower:
            return "Partnership Deed"
        elif "service" in text_lower or "master service" in text_lower:
            return "Service Contract"
        return "General Agreement"

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts entities like ORG, DATE, MONEY, GPE.
        """
        doc = self.nlp(text[:1000000]) # Limit to 1M chars for spacy
        entities = {
            "Parties": [],
            "Dates": [],
            "Amounts": [],
            "Jurisdiction": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG" or ent.label_ == "PERSON":
                entities["Parties"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["Dates"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["Amounts"].append(ent.text)
            elif ent.label_ == "GPE":
                entities["Jurisdiction"].append(ent.text)
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
            
        return entities

    def segment_clauses(self, text: str) -> List[str]:
        """
        Segments text into potential clauses based on common numbering patterns.
        """
        # Improved pattern to catch various clause headers
        clause_pattern = r'\n(?=\s*\d+\.|\s*[A-Z]\.|\s*Article\s+[IVXLCDM]+|\s*Section\s+\d+)'
        clauses = re.split(clause_pattern, text)
        
        # Remove duplicates and very short fragments that aren't meaningful clauses
        seen = set()
        cleaned = []
        for c in clauses:
            text_snippet = c.strip()
            # Further filtering: ensure it's not just a number or a very short phrase
            if text_snippet and text_snippet not in seen and len(text_snippet) > 40 and not re.fullmatch(r'^\s*(\d+\.?|[A-Z]\.?)\s*$', text_snippet):
                cleaned.append(text_snippet)
                seen.add(text_snippet)
        
        return cleaned
