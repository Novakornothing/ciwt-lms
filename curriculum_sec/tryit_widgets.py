"""Try-It widget configs for every Security concept section.

The ladder on this branch renders order, sort, and reveal. Richer families
(cia-classifier, hash-demo, phishing-inspector, log-triage, firewall-tester,
port-matcher, and the rest) are named here so a later widget host can bind them.
Every section still has a working order, sort, or reveal widget today.
"""
from curriculum_sec.assemble import TRYIT_WIDGETS

FAMILIES = sorted({row['family'] for row in TRYIT_WIDGETS})
