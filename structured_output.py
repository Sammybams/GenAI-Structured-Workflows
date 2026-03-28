## QUIZ GENERATION

essay_generation_schema = {
  "type": "json_schema",
  "json_schema": {
    "name": "essay_block",
    "strict": True,
    "schema": {
    "type": "object",
    "description": (
      "A block of essay-style questions. Each item is an open-response question where the model "
      "provides the authoritative answer/explanation. Return a JSON object with a 'questions' array."
    ),
    "additionalProperties": False,
    "required": ["questions"],
    "properties": {
      "questions": {
        "type": "array",
        "minItems": 1,
        "description": (
          "Array of essay question objects. Each item should include a unique id, the question text, "
          "and a substantive answer/explanation. Points are optional but recommended for scoring weight."
        ),
        "items": {
          "type": "object",
          "additionalProperties": False,
          "required": ["id", "question", "explanation"],
          "properties": {
            "id": {
              "type": "string",
              "description": "Unique question identifier within this block (e.g., 'q1', 'essay_01'). Keep IDs short and unique."
            },
            "question": {
              "type": "string",
              "description": (
                "The prompt for the essay question. Should be clear and specific (e.g., 'Define osmosis', "
                "'What is the difference between mitosis and meiosis?')."
              )
            },
            "explanation": {
              "type": "string",
              "description": (
                "The model-provided answer/explanation. For essay items this should be a clear, well-structured "
                "paragraph (or short essay) that answers the question—suitable as a model answer or rubric."
              )
            },
          },
          "examples": [
            {
              "id": "q1",
              "question": "Define osmosis and explain one biological example where it is important.",
              "explanation": "Osmosis is the passive movement of water molecules across a semipermeable membrane from a region of lower solute concentration to a region of higher solute concentration. In plant cells, osmosis helps maintain turgor pressure: when soil water is available, water moves into root cells by osmosis, keeping cells turgid and supporting the plant structure.",
            },
            {
              "id": "q2",
              "question": "What is the difference between mitosis and meiosis?",
              "explanation": "Mitosis produces two genetically identical daughter cells from a single parent cell and is used for growth and tissue repair; meiosis produces four genetically diverse gametes with half the chromosome number of the parent, used for sexual reproduction. Key differences include the number of cell divisions (one vs two), synapsis and crossing-over (present in meiosis), and the genetic outcome (identical vs varied).",
            }
          ]
        }
      }
    }
  }
  }
}


mcq_schema = {
  "type": "json_schema",
  "json_schema": {
    "name": "mcq_block",
    "strict": True,
    "schema": {
    "type": "object",
    "description": "A block of multiple-choice questions (MCQs). The model should return a JSON object with a 'questions' array containing one or more MCQ items.",
    "additionalProperties": False,
    "required": ["questions"],
    "properties": {
      "questions": {
        "type": "array",
        "minItems": 1,
        "description": (
          "Array of MCQ objects. Each item represents a single multiple-choice question. "
          "Use this block to generate one or more MCQs. Each question must include an id, "
          "question text, exactly 4 options, a zero-based answer_index, a short explanation, and points."
        ),
        "items": {
          "type": "object",
          "additionalProperties": False,
          "required": ["id", "question", "options", "answer_index", "explanation"],
          "properties": {
            "id": {
              "type": "string",
              "description": "Unique question identifier within this block (e.g., 'q1', 'mcq_01'). Keep IDs short and unique."
            },
            "question": {
              "type": "string",
              "description": (
                "The full question text presented to the student. Should be clear, self-contained, and not reveal the answer. "
                "For example: 'Which device stores electrical charge?'"
              )
            },
            "options": {
              "type": "array",
              "minItems": 4,
              "maxItems": 4,
              "description": (
                "Exactly 4 answer options (strings). Options should be concise (prefer <= 10 words), mutually plausible, "
                "and include one correct answer and three distractors."
              ),
              "items": {
                "type": "string",
                "description": "A single option string (one answer choice)."
              }
            },
            "answer_index": {
              "type": "integer",
              "minimum": 0,
              "maximum": 3,
              "description": (
                "Zero-based index (0..3) pointing to the correct option within the `options` array. "
                "Use integers only (do not supply the option text)."
              )
            },
            "explanation": {
              "type": "string",
              "description": (
                "A short student-facing explanation (1–2 sentences) explaining why the correct option is correct. "
                "Useful for feedback and review."
              )
            },
          },
          "examples": [
            {
              "id": "q1",
              "question": "Which component stores electrical charge?",
              "options": ["Resistor", "Capacitor", "Inductor", "Diode"],
              "answer_index": 1,
              "explanation": "A capacitor stores electrical charge on its plates separated by a dielectric.",
            }
          ]
        }
      }
    }
  }
  }
}
