"""Guardrails for the AI tutor: academic-integrity refusals and off-topic detection. Pending SME review."""
import re

CHEAT = [re.compile(p, re.I) for p in (
    r'\b(answers?|key|solutions?)\b.{0,40}\b(quiz|test|exam|midterm|final|assessment|graded)\b',
    r'\b(quiz|test|exam|midterm|final|assessment|graded)\b.{0,40}\b(answers?|key|solutions?)\b',
    r'\bwhich (option|answer|choice) is (right|correct)\b',
    r'\b(is it|answer is) (option |choice )?\(?[a-d]\)?\s*[?.!]?$',
    r'\b(give|tell|send) me (the|all the) answers?\b',
    r'\b(do|complete|finish|take) my (quiz|test|exam|lab|homework|assignment)\b',
    r'\bjust (give|tell) me the answer\b',
)]
CHEAT_REPLY = ('I can walk you through the concept, not give the graded quiz answer. Tell me which idea is confusing '
               '(for example “why does a 169.254 address mean no DHCP lease?”) and I will point you to the lesson section and '
               'explanations that teach it.')
OFFTOPIC_REPLY = ('I can only help with what this course teaches, and I could not find that in the lessons, explanations, '
                  'glossary or lab guides. Try asking about a lesson topic, a term, or a lab step.')
DISABLED_REPLY = 'Your instructor has turned the AI tutor off for this class.'


def is_cheating(q):
    return any(p.search(q or '') for p in CHEAT)


def on_topic(score, coverage, n_terms):
    """A question is answerable only when the course material clearly matches it."""
    if n_terms == 0:
        return False
    if n_terms == 1:
        return score >= 2.0 and coverage >= 1.0
    return score >= 3.0 and coverage >= 0.5
