# Leveraging Structured Output & Function Calling for Reliable GenAI Workflows

**Workshop Recording:** [Watch on YouTube](https://youtu.be/8_mKF9SLqFc)

## Overview

Stop over-engineering prompts to force JSON. This workshop demonstrates how to use **Structured Outputs** and **Function Calling** with Azure OpenAI to produce validated, machine-readable LLM responses you can wire directly into systems.

Using quiz generation as a case study, you'll learn:
- Schema design for guaranteed JSON structure
- Automatic validation without brittle prompt hacks
- Function-driven workflows for real-time data and computations

These techniques are applicable to:
- State management
- Classification tasks
- Automated grading
- LMS import/export
- Any production use case requiring reliable, structured AI responses

---

## Project Structure

```
function-calling/
├── main.py                 # FastAPI endpoints for all features
├── client.py               # Azure OpenAI client configuration
├── function_calling.py     # Function calling implementation
├── structured_output.py    # JSON schemas for quiz generation
├── prompts.yaml            # Function definitions in YAML
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 3. Run the API

```bash
uvicorn main:app --reload --port 8000
```

### 4. Access the API

- **Swagger UI:** http://localhost:8000/docs
- **Base URL:** http://localhost:8000

---

## API Endpoints

### Function Calling: `/chat`

**POST** `/chat` - Chat with function calling support for datetime and calculations.

```json
// Request
{
  "message": "What time is it and calculate 25 * 4 + 10"
}

// Response
{
  "response": "The current time is 5:52 PM, and the result of 25 × 4 + 10 is 110."
}
```

**Supported queries:**
- Datetime: "What time is it?", "What's today's date?", "What day is it?"
- Math: "Calculate sqrt(144)", "What's 2^10?", "15% of 200"

---

### Structured Output: `/generate/mcq`

**POST** `/generate/mcq` - Generate multiple choice questions with guaranteed JSON structure.

```json
// Request
{
  "topic": "Python programming",
  "num_questions": 3,
  "difficulty": "medium"
}

// Response
{
  "topic": "Python programming",
  "difficulty": "medium",
  "requested": 3,
  "returned": 3,
  "questions": [
    {
      "id": "q1",
      "question": "Which keyword is used to define a function in Python?",
      "options": ["function", "def", "func", "define"],
      "answer_index": 1,
      "explanation": "In Python, the 'def' keyword is used to define a function."
    }
  ]
}
```

---

### Structured Output: `/generate/essay`

**POST** `/generate/essay` - Generate essay questions with model answers.

```json
// Request
{
  "topic": "Machine Learning",
  "num_questions": 2,
  "difficulty": "hard"
}

// Response
{
  "topic": "Machine Learning",
  "difficulty": "hard",
  "requested": 2,
  "returned": 2,
  "questions": [
    {
      "id": "q1",
      "question": "Explain the bias-variance tradeoff in machine learning.",
      "explanation": "The bias-variance tradeoff describes the balance between..."
    }
  ]
}
```

---

## Key Concepts

### Structured Outputs

Structured Outputs guarantee that the model's response conforms to a JSON Schema you define. No more parsing errors or malformed JSON.

**Schema Structure for Azure OpenAI:**
```python
schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "mcq_block",
        "strict": True,
        "schema": {
            "type": "object",
            "required": ["questions"],
            "additionalProperties": False,
            "properties": {
                "questions": {
                    "type": "array",
                    "items": { ... }
                }
            }
        }
    }
}
```

**Usage:**
```python
response = client.chat.completions.create(
    model=deployment_name,
    messages=[...],
    response_format=mcq_schema  # Pass the schema here
)
```

**Benefits:**
- Guaranteed valid JSON every time
- No need for retry logic on malformed responses
- Direct integration with downstream systems
- Type-safe data for your application

---

### Function Calling

Function Calling allows the model to invoke predefined functions when needed, enabling real-time data retrieval and computations.

**How it works:**
1. Define functions with schemas (in `prompts.yaml`)
2. Pass function definitions to the API
3. Model decides when to call functions
4. Execute the function locally
5. Return results to the model for final response

**Example Flow:**
```
User: "What's 25 * 4 + 10?"
    ↓
Model: calls calculate(expression="25 * 4 + 10")
    ↓
Your code: executes eval("25 * 4 + 10") → "110"
    ↓
Model: "The result of 25 × 4 + 10 is 110."
```

**Function Definition (YAML):**
```yaml
functions:
  calculate:
    description: "Evaluate a mathematical expression"
    parameters:
      expression:
        type: string
        description: "The mathematical expression to evaluate"
```

---

## File Breakdown

### `client.py`
Azure OpenAI client initialization using environment variables.

### `structured_output.py`
JSON Schemas for MCQ and Essay question generation with:
- Strict validation (`additionalProperties: False`)
- Required fields enforcement
- Type constraints (arrays, integers, strings)
- Value constraints (min/max for answer_index)

### `function_calling.py`
- Function implementations (`get_current_datetime`, `calculate`)
- Schema generation from YAML config
- Full conversation loop handling tool calls

### `prompts.yaml`
Declarative function definitions—easy to modify without code changes.

### `main.py`
FastAPI application with:
- Pydantic models for request/response validation
- Three endpoints: `/chat`, `/generate/mcq`, `/generate/essay`
- Error handling and response filtering

---

## Production Use Cases

| Use Case | Implementation |
|----------|---------------|
| **Quiz Generation** | Structured output with MCQ/Essay schemas |
| **Automated Grading** | Compare student answers against `answer_index` |
| **LMS Import** | JSON output ready for QTI/SCORM conversion |
| **Classification** | Structured output with enum constraints |
| **Real-time Data** | Function calling for APIs, databases, calculations |
| **State Management** | Structured output for consistent state objects |
| **Chatbots with Actions** | Function calling for bookings, lookups, etc. |

---

## Tips for Schema Design

1. **Use `strict: True`** - Ensures model follows schema exactly
2. **Set `additionalProperties: False`** - Prevents extra fields
3. **Define `required` arrays** - Guarantees essential fields
4. **Add descriptions** - Helps the model understand intent
5. **Include examples** - Improves output quality
6. **Use constraints** - `minimum`, `maximum`, `enum` for validation

---

## Resources

- [Azure OpenAI Structured Outputs Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/structured-outputs)
- [Azure OpenAI Function Calling Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling)
- [OpenAI JSON Schema Guide](https://platform.openai.com/docs/guides/structured-outputs)

---

## License

MIT License - Feel free to use this code for your projects.

---

**Questions?** Watch the [full workshop recording](https://youtu.be/8_mKF9SLqFc) for detailed explanations and live demos.
