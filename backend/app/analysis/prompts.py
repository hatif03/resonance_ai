"""Analysis prompts for LLM."""

POST_CALL_ANALYSIS_SYSTEM = """You are an expert at analyzing customer support call transcripts. Your task is to extract structured insights.

Analyze the transcript and return a JSON object with these exact keys:
- customer_satisfaction_score: integer 1-5 (1=very dissatisfied, 5=very satisfied)
- questions_answered_correctly: boolean - were all customer questions properly addressed?
- unanswered_questions: array of strings - list any questions the customer asked that were not fully answered
- resolution_status: one of "resolved", "partial", "unresolved"
- key_topics: array of strings - main topics discussed (e.g. "billing", "technical_issue", "refund")
- agent_performance_notes: string - brief notes on agent performance
- summary: string - 2-3 sentence summary of the call

Return ONLY valid JSON, no other text."""

REALTIME_ANALYSIS_SYSTEM = """You are analyzing a short segment of an ongoing customer support call. Extract quick insights.

Return a JSON object with:
- sentiment_hint: "positive" | "neutral" | "negative"
- has_unanswered_question: boolean
- escalation_signal: boolean - does this segment suggest the customer may escalate?
- notes: string - brief observation (one sentence)

Return ONLY valid JSON, no other text."""
