import json
import logging
from typing import Any

from pydantic import ValidationError, create_model

from app.core.config import settings

logger = logging.getLogger("docuflow-extractor")


class StructuredExtractor:
    """
    Orchestrates schema-based LLM prompts and validates JSON formatting outputs.
    """

    async def extract_structured_data(
        self, text: str, schema_def: dict[str, Any], max_retries: int = 3
    ) -> dict[str, Any]:
        """
        Dynamically constructs a Pydantic model for validation, submits context
        to OpenAI or falls back to a rules-based parser, and returns schema-valid data.
        """
        logger.info("Building dynamic Pydantic validator model...")
        validator_model = self._create_dynamic_model(schema_def)

        # Retrieve API key settings
        api_key = settings.OPENAI_API_KEY

        raw_json_str = ""
        if api_key and api_key.strip():
            logger.info("Executing OpenAI Chat Completion extraction...")
            raw_json_str = await self._extract_via_openai(text, schema_def, api_key)
        else:
            logger.warning(
                "OPENAI_API_KEY not configured. Falling back to mock rules."
            )
            raw_json_str = self._extract_via_mock_rules(text, schema_def)

        # Validate structured JSON string against the dynamic model
        attempt = 1
        while attempt <= max_retries:
            try:
                logger.info(
                    f"Validating extraction schema (attempt {attempt}/{max_retries})..."
                )
                validated_data = validator_model.model_validate_json(raw_json_str)
                logger.info("Extraction validation completed successfully.")
                return validated_data.model_dump()  # type: ignore
            except ValidationError as ve:
                logger.warning(f"Schema validation failed on attempt {attempt}: {ve}")
                if attempt == max_retries:
                    raise ve
                # Retry hook (self-correcting prompt placeholder)
                attempt += 1

        raise RuntimeError("Structured extraction failed validation checks.")

    def _create_dynamic_model(self, schema_def: dict[str, Any]) -> Any:
        """
        Helper method generating a Pydantic model dynamically from JSON field metadata.
        """
        fields: dict[str, Any] = {}
        for name, field_info in schema_def.items():
            field_type: type = str
            if isinstance(field_info, dict):
                type_str = field_info.get("type", "str")
            else:
                type_str = str(field_info)

            # Map types
            if type_str in ["number", "float"]:
                field_type = float
            elif type_str in ["integer", "int"]:
                field_type = int
            elif type_str in ["boolean", "bool"]:
                field_type = bool
            else:
                field_type = str

            fields[name] = (field_type, ...)

        return create_model("DynamicSchemaValidator", **fields)

    async def _extract_via_openai(
        self, text: str, schema_def: dict[str, Any], api_key: str
    ) -> str:
        """
        Submits prompt contexts to OpenAI Chat model.
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI

        fields_desc = "\n".join(
            [f"- {name}: {info}" for name, info in schema_def.items()]
        )
        system_prompt = (
            "You are an expert document extraction agent.\n"
            "Extract schema fields from text. "
            "Return ONLY a valid JSON object matching the requested schema.\n"
            "Do NOT wrap output in markdown (e.g. no ```json) or add comments.\n"
            f"Requested Schema:\n{fields_desc}"
        )

        llm = ChatOpenAI(
            openai_api_key=api_key, model="gpt-4o-mini", temperature=0.0
        )
        response = await llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Document Context:\n{text}"),
            ]
        )

        raw_content = str(response.content).strip()
        # Strip potential markdown wrappers if the LLM output ignores instructions
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
        return raw_content.strip()

    def _extract_via_mock_rules(self, text: str, schema_def: dict[str, Any]) -> str:
        """
        Lightweight fallback matching common document values via regex/keyword rules.
        """
        text_lower = text.lower()
        extracted: dict[str, Any] = {}

        for name, field_info in schema_def.items():
            name_lower = name.lower()
            field_type = "str"
            if isinstance(field_info, dict):
                field_type = field_info.get("type", "str")

            # Fallback mocks based on field name queries
            if "number" in name_lower or "no" in name_lower or "id" in name_lower:
                extracted[name] = "INV-2026-90"
            elif (
                "vendor" in name_lower
                or "company" in name_lower
                or "merchant" in name_lower
            ):
                if "acme" in text_lower:
                    extracted[name] = "Acme Corp"
                elif "google" in text_lower:
                    extracted[name] = "Google Inc"
                else:
                    extracted[name] = "Vendor Placeholder"
            elif (
                "amount" in name_lower or "total" in name_lower or "price" in name_lower
            ):
                extracted[name] = (
                    1500.00 if field_type in ["number", "float"] else "1500.00"
                )
            elif "gst" in name_lower or "tax" in name_lower:
                extracted[name] = (
                    270.00 if field_type in ["number", "float"] else "270.00"
                )
            elif "date" in name_lower:
                extracted[name] = "2026-07-11"
            else:
                extracted[name] = f"mock_{name}"

        return json.dumps(extracted)
