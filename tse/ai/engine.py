from typing import Dict, Any, Optional
from tse.ai.client import ai_client
from tse.ai.modes import get_exam_instructions
from tse.utils.logger import logger

class PromptEngine:
    def __init__(self):
        pass

    def generate_exam_answer(
        self,
        question: str,
        subject: str,
        mode: str,
        marks: int,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds the prompts and calls the AI client to generate an exam-ready answer.
        Returns a dictionary containing the answer, provider, and model used.
        """
        marking_rules = get_exam_instructions(mode, marks)
        
        # Build subject adaptation instruction
        subject_adaptation = ""
        sub_lower = subject.lower()
        if "dbms" in sub_lower or "mongodb" in sub_lower or "database" in sub_lower:
            subject_adaptation = "For this database subject, include schemas, tables, relationships, and clean SQL queries (or MongoDB documents if applicable)."
        elif "network" in sub_lower:
            subject_adaptation = "For this computer networks subject, mention standard network models (OSI/TCP-IP layers), protocol names, packet structures, or socket details where relevant."
        elif "operating" in sub_lower or "os" == sub_lower:
            subject_adaptation = "For this operating systems subject, focus on kernel vs user space, process state transitions, CPU scheduling algorithms, memory paging, and hardware interactions."
        elif "algorithm" in sub_lower or "daa" in sub_lower:
            subject_adaptation = "For this algorithms subject, provide clean pseudocode, dry run tables, and analyze time/space complexity using Big-O notation."
        elif "math" in sub_lower:
            subject_adaptation = "For this mathematics subject, provide step-by-step derivations, clarify formulas, define variables, and show calculations clearly."
        elif "ai" in sub_lower or "ml" in sub_lower or "machine learning" in sub_lower:
            subject_adaptation = "For this AI/ML subject, include mathematical modeling, cost functions, training processes, and explain input/output features clearly."

        system_prompt = (
            "You are an elite Engineering Professor and Academic Mentor. Your task is to provide high-quality, "
            f"exam-ready answers for the subject '{subject}'.\n\n"
            f"{subject_adaptation}\n\n"
            "Format the response using Markdown. The response MUST contain these specific sections:\n"
            "- Definition (Clear, formal academic definition)\n"
            "- Explanation (Conceptual breakdown)\n"
            "- Example (A concrete engineering example or case study)\n"
            "- Keywords (List of critical technical terms)\n"
            "- Exam Ready Answer (A structured, bulleted answer optimized for the examiner)\n"
            "- Memory Trick (A mnemonic or association technique to memorize this concept)\n"
            "- Expected Marks (Brief explanation of how marks are awarded for this topic, e.g., 2 marks for definition, 3 marks for diagram)\n"
            "- Previous Related Questions (Give 2 examples of how this topic is asked in past papers)\n"
            "- Revision Tips (A checklist to review this concept in 2 minutes)\n\n"
            "Here are the marking guidelines you must follow:\n"
            f"{marking_rules}\n"
        )

        if context:
            system_prompt += (
                "\nCRITICAL INSTRUCTION:\n"
                "You have been provided with context retrieved from the student's textbooks/PDF documents.\n"
                "You MUST answer the question STRICTLY using the context below. Do not use external knowledge.\n"
                "If the context does not contain the answer, you must state: "
                "'The answer could not be found in the uploaded documents.'\n\n"
                f"=== PDF DOCUMENT CONTEXT ===\n{context}\n===========================\n"
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Subject: {subject}\nTarget Marks: {marks}\nQuestion: {question}"}
        ]

        logger.info(f"Generating answer for: '{question}' | Subject: {subject} | Mode: {mode} | Marks: {marks}")
        
        raw_answer, final_provider, final_model = ai_client.generate_completion(
            messages=messages,
            provider=provider,
            model=model
        )

        return {
            "answer": raw_answer,
            "provider": final_provider,
            "model": final_model
        }

    def generate_quiz(self, subject: str, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Generates a raw JSON list containing 5 quiz questions for a subject."""
        system_prompt = (
            "You are an expert examiner. Generate 5 multiple-choice questions (MCQs) for the subject "
            f"'{subject}'. The response must be a valid JSON array of objects. Do not include markdown code block formatting (like ```json), just raw JSON.\n"
            "Each object must have the following keys:\n"
            "- 'question': the question text\n"
            "- 'option_a': first option\n"
            "- 'option_b': second option\n"
            "- 'option_c': third option\n"
            "- 'option_d': fourth option\n"
            "- 'correct_option': single character string: 'A', 'B', 'C', or 'D'\n"
            "- 'explanation': a brief explanation of why the correct option is correct\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate 5 MCQs for {subject}."}
        ]
        
        raw_res, _, _ = ai_client.generate_completion(messages, provider, model)
        # Strip any code blocks if the LLM outputted them anyway
        raw_res = raw_res.strip()
        if raw_res.startswith("```"):
            lines = raw_res.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_res = "\n".join(lines).strip()
            
        return raw_res

    def generate_flashcards(self, subject: str, topic: str, count: int = 5, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Generates a list of flashcards for a subject and topic."""
        system_prompt = (
            f"You are an expert tutor. Generate {count} flashcards for the subject '{subject}' focusing on the topic '{topic}'.\n"
            "The output must be a valid JSON array of objects. Do not include markdown code blocks, just raw JSON.\n"
            "Each object must have the following keys:\n"
            "- 'question': the question or concept on the front of the flashcard\n"
            "- 'answer': the explanation or definition on the back of the flashcard\n"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate {count} flashcards."}
        ]
        raw_res, _, _ = ai_client.generate_completion(messages, provider, model)
        raw_res = raw_res.strip()
        if raw_res.startswith("```"):
            lines = raw_res.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_res = "\n".join(lines).strip()
        return raw_res

prompt_engine = PromptEngine()
