import os
import json
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    """
    Handles deep legal reasoning using GPT-4 or Claude 3.
    """
    def __init__(self, provider="openai"):
        self.provider = provider
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4-turbo"
        elif provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-opus-20240229"

    def analyze_clause(self, clause_text: str, contract_type: str):
        """
        Analyzes a single clause for risk and provides a plain language explanation.
        """
        prompt = f"""
        You are a legal expert for Indian SMEs. Analyze the following clause from a {contract_type}.
        
        Clause Text: "{clause_text}"
        
        Provide the output in valid JSON format with the following keys:
        - "explanation": A plain-language explanation of what this clause means for a business owner.
        - "risk_level": "Low", "Medium", or "High".
        - "risk_reason": Why is this risky (or not)?
        - "suggestion": How can this be renegotiated to be more SME-friendly?
        - "category": (e.g., Liability, Termination, Payment, IP, etc.)
        """
        
        return self._get_completion(prompt)

    def summarize_contract(self, full_text: str, contract_type: str):
        """
        Generates a high-level summary and composite risk score.
        """
        prompt = f"""
        Analyze this {contract_type} and provide a summary for a business owner.
        
        Contract Text: {full_text[:5000]}... (truncated)
        
        Provide the output in valid JSON format with the following keys:
        - "summary": A brief (3-4 bullet points) summary of the key obligations.
        - "composite_risk_score": An integer from 1-10 (10 being highest risk).
        - "top_risks": List of top 3 risky areas identified.
        - "missing_clauses": Any standard clauses missing that should be there for Indian SMEs.
        """
        return self._get_completion(prompt)

    def detect_hindi_and_translate(self, text: str):
        """
        Detects if text is in Hindi and provides a semantic English translation.
        """
        prompt = f"""
        The following text might be in Hindi or a mix of English and Hindi.
        1. Detect the language.
        2. Translate it into professional English legal terminology while keeping the semantic meaning intact.
        
        Text: "{text}"
        
        Output format: JSON with "language" and "translated_text".
        """
        return self._get_completion(prompt)

    def _get_completion(self, prompt: str):
        # Check for placeholder or missing keys
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_" in api_key:
            return self._get_simulated_response(prompt)
            
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            elif self.provider == "anthropic":
                # Simulated for Anthropic as well if key is missing
                if not os.getenv("ANTHROPIC_API_KEY") or "your_" in os.getenv("ANTHROPIC_API_KEY"):
                    return self._get_simulated_response(prompt)
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return self._get_simulated_response(prompt)
        return None

    def _get_simulated_response(self, prompt: str):
        """Returns a realistic mock response for demo purposes when API keys are missing."""
        if "analyze the following clause" in prompt.lower():
            # Extract clause text for basic heuristic simulation
            clause_text = prompt.split('Clause Text: "')[1].split('"')[0].lower() if 'Clause Text: "' in prompt else ""
            
            if "payment" in clause_text or "fee" in clause_text or "price" in clause_text:
                return {
                    "explanation": "[DEMO MODE] This clause outlines the payment obligations, including deadlines and potential interest for late payments.",
                    "risk_level": "Medium",
                    "risk_reason": "Vague payment timelines can lead to cash flow issues for SMEs.",
                    "suggestion": "Specify 'Payment within 30 days of invoice date' to ensure predictable cash flow.",
                    "category": "Payment Terms"
                }
            elif "terminate" in clause_text or "cancellation" in clause_text:
                return {
                    "explanation": "[DEMO MODE] This section defines how and when the agreement can be ended by either party.",
                    "risk_level": "High",
                    "risk_reason": "One-sided termination rights can leave an SME vulnerable after making investments.",
                    "suggestion": "Negotiate mutual termination for convenience with a 60-day notice period.",
                    "category": "Termination"
                }
            elif "liability" in clause_text or "indemnify" in clause_text:
                return {
                    "explanation": "[DEMO MODE] This clause limits or assigns financial responsibility for damages or losses.",
                    "risk_level": "High",
                    "risk_reason": "Unlimited liability clauses are high-risk for SMEs and can lead to business failure.",
                    "suggestion": "Limit total liability to the amount paid under the contract in the last 12 months.",
                    "category": "Liability & Indemnity"
                }
            elif "intellectual property" in clause_text or "ip" in clause_text or "copyright" in clause_text:
                return {
                    "explanation": "[DEMO MODE] Defines ownership of work results and pre-existing assets.",
                    "risk_level": "Medium",
                    "risk_reason": "Broad IP transfers might strip the SME of its core technology or methodology.",
                    "suggestion": "Ensure the SME retains ownership of its background IP and only licenses it for the project.",
                    "category": "Intellectual Property"
                }
            else:
                return {
                    "explanation": "[DEMO MODE] This clause covers general administrative or standard operating procedures of the agreement.",
                    "risk_level": "Low",
                    "risk_reason": "Seems to be standard boilerplate language with minimal commercial risk.",
                    "suggestion": "Verify that the governing law is set to your local jurisdiction (e.g., Delhi or Mumbai).",
                    "category": "General Provisions"
                }
        elif "analyze this" in prompt.lower() and "summary" in prompt.lower():
            return {
                "summary": [
                    "General business obligation to provide services on time.",
                    "Standard payment terms (30 days credit).",
                    "Mutual confidentiality agreement included.",
                    "Termination requires 30 days written notice."
                ],
                "composite_risk_score": 4,
                "top_risks": ["Vague IP transfer terms", "Missing arbitration city"],
                "missing_clauses": ["Force Majeure", "Severability Clause"]
            }
        elif "hindi" in prompt.lower():
            return {
                "language": "Hindi (Simulated)",
                "translated_text": "This is a simulated translation of your Hindi contract text for demonstration purposes."
            }
        return {"error": "Key missing. Please add OPENAI_API_KEY to .env"}
