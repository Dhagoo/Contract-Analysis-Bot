from .parser import ContractParser
from .nlp_engine import NLPEngine
from .llm_engine import LLMEngine
import json
import os
from datetime import datetime

class LegalAssistantBackend:
    """
    Orchestrates the parsing, NLP analysis, and LLM reasoning.
    """
    def __init__(self, llm_provider="openai"):
        self.parser = ContractParser()
        self.nlp = NLPEngine()
        self.llm = LLMEngine(provider=llm_provider)
        
        # Paths relative to project root
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.logs_dir = os.path.join(self.root_dir, "logs")
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def process_contract(self, file_path: str):
        """
        Full pipeline: Parse -> Classify -> NER -> Segment -> LLM Analysis.
        """
        # 1. Extraction
        text = self.parser.get_text(file_path)
        if "Error" in text or "Unsupported" in text:
            return {"error": text}

        # 2. Language Handling
        # Preliminary check for Hindi characters
        if any('\u0900' <= char <= '\u097F' for char in text):
            translation_info = self.llm.detect_hindi_and_translate(text[:2000]) # Sample for detection
            if translation_info.get("language") == "Hindi":
                # For full processing, we'd translate the whole doc or process via LLM directly
                # For now, we flag it and let the LLM handle the summary/analysis knowing it's Hindi
                pass

        # 3. Classification & Basic Entities
        contract_type = self.nlp.classify_contract(text)
        entities = self.nlp.extract_entities(text)
        
        # 4. Summary & Global Risk (LLM)
        summary_data = self.llm.summarize_contract(text, contract_type)
        
        # 4. Clause Analysis (LLM - limited to top clauses for performance/cost)
        clauses = self.nlp.segment_clauses(text)
        
        detailed_analysis = []
        for clause in clauses[:15]: # Process top 15 meaningful clauses
            analysis = self.llm.analyze_clause(clause, contract_type)
            detailed_analysis.append({
                "original_text": clause,
                "analysis": analysis
            })

        # 5. Audit Log
        report = {
            "timestamp": datetime.now().isoformat(),
            "filename": os.path.basename(file_path),
            "contract_type": contract_type,
            "entities": entities,
            "summary": summary_data,
            "clause_analysis": detailed_analysis
        }
        
        self._log_audit(report)
        
        return report

    def _log_audit(self, report):
        log_file = os.path.join(self.logs_dir, "audit_trail.json")
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(report)
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=4)
