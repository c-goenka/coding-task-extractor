"""
TaskExtractor: Multi-stage LLM extraction with confidence scoring.

Stage 1: Binary classification (YES/NO programming study)
Stage 2: Task extraction (raw details) - TODO
Stage 3: Categorization (structured output) - TODO
"""

import re
import sys
import os
import time
from typing import Optional, Tuple

from ..models.task_models import Paper, TaskExtractionResult, TaskCategories
from ..prompts.binary_classification import BinaryClassificationPrompt
from ..prompts.task_extraction import TaskExtractionPrompt
from ..prompts.categorization import CategorizationPrompt

# Import LangChain components
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    print("Warning: LangChain not available. Install with: pip install langchain langchain-openai")


class TaskExtractor:
    """Extracts coding tasks using multi-stage LLM approach."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        """Initialize the task extractor."""
        self.model = model
        self.temperature = temperature

        # Initialize LLM if available
        try:
            self.llm = ChatOpenAI(model=model, temperature=temperature)
            self.llm_available = True
        except Exception as e:
            print(f"Warning: Could not initialize LLM: {e}")
            self.llm_available = False

    def _parse_binary_response(self, response: str) -> Tuple[bool, float, str]:
        """Parse the binary classification response."""
        try:
            # Extract decision
            decision_match = re.search(r'Decision:\s*(YES|NO)', response, re.IGNORECASE)
            has_coding_task = decision_match.group(1).upper() == 'YES' if decision_match else False

            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*([\d.]+)', response)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5

            # Extract reason
            reason_match = re.search(r'Reason:\s*(.+)', response)
            reason = reason_match.group(1).strip() if reason_match else "Could not parse reasoning"

            return has_coding_task, confidence, reason

        except Exception as e:
            return False, 0.0, f"Error parsing response: {str(e)}"

    def classify_paper_binary(self, paper: Paper) -> TaskExtractionResult:
        """
        Stage 1: Binary classification - is this a programming user study?
        """
        if not self.llm_available:
            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=False,
                confidence=0.0,
                extraction_reason="LLM not available"
            )

        try:
            # Rate limiting
            time.sleep(0.5)

            # Format the prompt
            prompt_data = BinaryClassificationPrompt.format_prompt(
                title=paper.title,
                abstract=paper.abstract or "No abstract available"
            )

            # Create LangChain prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_data["system"]),
                ("human", prompt_data["user"])
            ])

            # Create chain
            chain = prompt | self.llm | StrOutputParser()

            # Get response
            response = chain.invoke({})

            # Parse response
            has_coding_task, confidence, reason = self._parse_binary_response(response)

            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=has_coding_task,
                confidence=confidence,
                raw_task_description=response if has_coding_task else None,
                extraction_reason=reason
            )

        except Exception as e:
            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=False,
                confidence=0.0,
                extraction_reason=f"Error in classification: {str(e)}"
            )

    def _parse_task_extraction(self, response: str) -> dict:
        """Parse the task extraction response."""
        try:
            result = {}
            lines = response.strip().split('\n')

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    result[key] = value

            return result
        except Exception as e:
            return {"error": f"Failed to parse response: {str(e)}"}

    def extract_task_details(self, paper: Paper) -> TaskExtractionResult:
        """
        Stage 2: Extract detailed task information for programming papers.
        """
        if not self.llm_available:
            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=False,
                confidence=0.0,
                extraction_reason="LLM not available"
            )

        try:
            # Rate limiting
            time.sleep(0.5)

            # Format the prompt
            prompt_data = TaskExtractionPrompt.format_prompt(
                title=paper.title,
                abstract=paper.abstract or "No abstract available"
            )

            # Create LangChain prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_data["system"]),
                ("human", prompt_data["user"])
            ])

            # Create chain
            chain = prompt | self.llm | StrOutputParser()

            # Get response
            response = chain.invoke({})

            # Parse response
            parsed = self._parse_task_extraction(response)
            confidence = float(parsed.get('confidence', 0.5))

            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=True,  # Only called for papers that passed binary classification
                confidence=confidence,
                raw_task_description=response,
                extraction_reason=parsed.get('task_description', 'Task extraction completed')
            )

        except Exception as e:
            return TaskExtractionResult(
                paper_id=paper.paper_id,
                has_coding_task=False,
                confidence=0.0,
                extraction_reason=f"Error in task extraction: {str(e)}"
            )

    def categorize_task(self, task_details: str) -> Optional[TaskCategories]:
        """
        Stage 3: Categorize the extracted task into structured format.
        """
        if not self.llm_available:
            return None

        try:
            # Rate limiting
            time.sleep(0.5)

            # Format the prompt
            prompt_data = CategorizationPrompt.format_prompt(task_details)

            # Create LangChain prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_data["system"]),
                ("human", prompt_data["user"])
            ])

            # Create chain with structured output
            structured_llm = self.llm.with_structured_output(TaskCategories)
            chain = prompt | structured_llm

            # Get structured response
            result = chain.invoke({})

            return result

        except Exception as e:
            print(f"Error in categorization: {str(e)}")
            return None

    # Convenience methods for testing
    def test_binary_classification(self, papers: list) -> list:
        """Test binary classification on a list of papers."""
        results = []
        for paper in papers:
            result = self.classify_paper_binary(paper)
            results.append(result)
            print(f"Paper {paper.paper_id}: {'YES' if result.has_coding_task else 'NO'} ({result.confidence:.2f}) - {result.extraction_reason}")
        return results
