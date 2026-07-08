def get_exam_instructions(mode: str, marks: int) -> str:
    """Returns specific marking guidelines and structural requirements for the AI prompt based on mode/marks."""
    mode = mode.lower()
    
    if mode == "mcq":
        return (
            "Format the output strictly as a Multiple Choice Question.\n"
            "Include:\n"
            "1. The Question\n"
            "2. Four Options: A, B, C, D\n"
            "3. Correct Option (e.g., Correct Option: A)\n"
            "4. Detailed Explanation of why it is correct and why other options are incorrect."
        )
    elif mode == "true_false":
        return (
            "Format the output strictly as a True/False Question.\n"
            "Include:\n"
            "1. The Statement\n"
            "2. Answer: True or False\n"
            "3. Comprehensive Explanation justifying the answer with core concepts."
        )
    elif mode == "short_notes":
        return (
            "Format the response as a Short Note (ideal for 3-5 marks).\n"
            "Structure:\n"
            "- Definition: 1-2 sentence core definition.\n"
            "- Key Concepts: 4-5 bullet points explaining the core mechanism.\n"
            "- Applications: Practical fields where this is used.\n"
            "- Pros & Cons: Quick comparison table of advantages and disadvantages."
        )
    
    # Marks-based theoretical answers
    if marks <= 2:
        return (
            "Format the response strictly for a 2 Marks Exam Question.\n"
            "Guidelines:\n"
            "- Be highly concise (maximum 100-150 words).\n"
            "- Start with a clear 1-sentence Definition.\n"
            "- Provide 2 clear, distinct bullet points of Explanation.\n"
            "- Give 1 quick Example.\n"
            "- Focus on high impact keywords."
        )
    elif marks <= 5:
        return (
            "Format the response for a 5 Marks Exam Question.\n"
            "Guidelines:\n"
            "- Medium length (200-350 words).\n"
            "- Provide a formal Definition.\n"
            "- Explain the core mechanism in 4-5 structured points.\n"
            "- Use a Markdown table or text-based diagram mapping to illustrate the concept.\n"
            "- Provide 1-2 practical Examples.\n"
            "- Highlight key technical vocabulary."
        )
    elif marks <= 10:
        return (
            "Format the response for a 10 Marks Exam Question.\n"
            "Guidelines:\n"
            "- Comprehensive, detailed answer (450-600 words).\n"
            "- Sections required: Definition, Detailed Explanation, Key Architecture/Components (with text representation if helpful), Comparison Table, Code/Math/Practical Example, Memory Trick (mnemonic), and 3 Quick Revision Points.\n"
            "- Must look professional, structured, and ready to write in a university answer sheet."
        )
    else:  # 15 Marks or Long Answer
        return (
            "Format the response for a 15 Marks (or Long Answer) Exam Question.\n"
            "Guidelines:\n"
            "- Exhaustive, deep-dive academic answer (700-1000 words).\n"
            "- Include:\n"
            "  1. Abstract / Introduction\n"
            "  2. Formal Definition\n"
            "  3. In-depth Explanation of sub-components and processes\n"
            "  4. Comprehensive Comparison Table with competing technologies/concepts\n"
            "  5. Architectural Diagram / Text-based flow representation\n"
            "  6. Multi-scenario Examples / Case Studies\n"
            "  7. Memory Trick (to help remember lists of points)\n"
            "  8. Common Pitfalls / Expected Marks breakdown\n"
            "  9. Brief Summary / Conclusion"
        )
