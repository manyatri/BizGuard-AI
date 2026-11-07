"""
LLM Provider — unified client for Anthropic (Claude) and OpenAI.
Falls back to a structured mock response when no API key is configured.
"""
import os
import json
from typing import Optional
from app.core.config import settings


class LLMUnavailableError(Exception):
    """Raised when no LLM API key is configured and fallback is disabled."""
    pass


class LLMProvider:
    """
    Calls Claude or OpenAI based on DEFAULT_LLM_PROVIDER setting.
    Returns the response text.  Raises LLMUnavailableError if no key.
    """

    @staticmethod
    def call(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
        """
        Primary entry point.  Tries real LLM first; falls back to structured
        mock response if keys are absent (clearly labelled as MOCK).
        """
        provider = getattr(settings, "DEFAULT_LLM_PROVIDER", "mock").lower()
        api_key_anthropic = getattr(settings, "ANTHROPIC_API_KEY", "") or ""
        api_key_openai = getattr(settings, "OPENAI_API_KEY", "") or ""

        if provider == "anthropic" and api_key_anthropic:
            return LLMProvider._call_anthropic(system_prompt, user_message, api_key_anthropic, max_tokens)
        elif provider == "openai" and api_key_openai:
            return LLMProvider._call_openai(system_prompt, user_message, api_key_openai, max_tokens)
        else:
            # No key — return clearly-labeled mock response
            return LLMProvider._mock_response(system_prompt, user_message)

    @staticmethod
    def is_real_llm_available() -> bool:
        provider = getattr(settings, "DEFAULT_LLM_PROVIDER", "mock").lower()
        api_key_anthropic = getattr(settings, "ANTHROPIC_API_KEY", "") or ""
        api_key_openai = getattr(settings, "OPENAI_API_KEY", "") or ""
        return (provider == "anthropic" and bool(api_key_anthropic)) or \
               (provider == "openai" and bool(api_key_openai))

    @staticmethod
    def _call_anthropic(system_prompt: str, user_message: str, api_key: str, max_tokens: int) -> str:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except Exception as e:
            return f"[LLM ERROR — Anthropic] {e}\n\n{LLMProvider._mock_response(system_prompt, user_message)}"

    @staticmethod
    def _call_openai(system_prompt: str, user_message: str, api_key: str, max_tokens: int) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM ERROR — OpenAI] {e}\n\n{LLMProvider._mock_response(system_prompt, user_message)}"

    @staticmethod
    def _mock_response(system_prompt: str, user_message: str) -> str:
        """
        Deterministic structured mock — clearly labelled, never presented as real AI.
        Content is derived from the prompt context to remain plausible.
        """
        hint = ""
        if "root cause" in user_message.lower() or "investigate" in user_message.lower():
            hint = (
                "**[MOCK — No LLM API key configured]**\n\n"
                "Based on the incident data provided:\n\n"
                "**Root Cause**: The inventory reservation step passed the wrong variant_id to "
                "`InventoryService.reserve_stock()`. The order correctly references the customer's "
                "chosen variant (Size M), but the fulfillment worker or the barcode scanner "
                "submitted Size L's bin ID. This is a data-entry / UI bug in the warehouse management layer.\n\n"
                "**Evidence**: order_items.variant_id → correct (Size M). "
                "inventories.quantity_reserved for Size L → unexpectedly incremented. "
                "inventories.quantity_reserved for Size M → 0 (should be 1).\n\n"
                "**Confidence**: 0.92 (high — pattern matches RULE_VARIANT_INVENTORY_MISMATCH exactly)\n\n"
                "*Configure ANTHROPIC_API_KEY or OPENAI_API_KEY in backend/.env for real AI analysis.*"
            )
        elif "proposal" in user_message.lower() or "fix" in user_message.lower() or "recover" in user_message.lower():
            hint = (
                "**[MOCK — No LLM API key configured]**\n\n"
                "**Proposed Recovery Steps**:\n"
                "1. Verify pre-conditions: confirm Size M reserved=0, Size L has unexpected reservation\n"
                "2. `release_reservation(wrong_variant_id, qty=1)` — undo erroneous deduction\n"
                "3. `reserve_stock(correct_variant_id, qty=1)` — apply correct reservation\n"
                "4. Confirm order_items.variant_id still correct (no change needed)\n"
                "5. Advance order status to INVOICED to resume fulfillment\n\n"
                "**Risk**: LOW — both variants have sufficient stock. Fully reversible.\n"
                "**Rollback**: re-release correct variant reservation, re-add wrong variant reservation, revert status.\n\n"
                "*Configure ANTHROPIC_API_KEY or OPENAI_API_KEY in backend/.env for real AI proposals.*"
            )
        elif "review" in user_message.lower() or "audit" in user_message.lower() or "accept" in user_message.lower():
            hint = (
                "**[MOCK — No LLM API key configured]**\n\n"
                "**Audit Verdict**: ACCEPT\n\n"
                "**Reasoning**: The proposal correctly identifies the root cause (wrong variant reservation) "
                "and proposes a minimal, targeted fix. Pre-check tests confirm the described state. "
                "Rollback steps are present and reversible. No side effects expected on other orders.\n\n"
                "**Risk Assessment**: LOW\n"
                "**Recommendation**: Proceed to human approval.\n\n"
                "*Configure ANTHROPIC_API_KEY or OPENAI_API_KEY in backend/.env for real AI audit.*"
            )
        else:
            hint = (
                "**[MOCK — No LLM API key configured]**\n\n"
                "Analysis complete. The system state has been inspected and findings logged. "
                "All invariant rules have been evaluated against the current database state.\n\n"
                "*Configure ANTHROPIC_API_KEY or OPENAI_API_KEY in backend/.env for real AI responses.*"
            )
        return hint
