import re

InjectionRule = tuple[str, str, str]

IGNORE_PRIOR = r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|commands|directions)"
ROLE_ESCAPE = r"(?i)(you\s+are\s+(now|not\s+an?\s+ai|a\s+human)|act\s+as\s+(if|though))"
PROMPT_LEAK = (
    r"(?i)(output\s+(your|the\s+full|entire)\s+(system\s+)?prompt"
    r"|reveal\s+(your\s+)?instructions"
    r"|show\s+me\s+(the\s+)?system)"
)
DELIMITER_BREAK = r"(?i)(forget\s+(about\s+)?the\s+(above|previous)|new\s+instruction|override\s+mode)"

DIRECT_INJECTION_PATTERNS: list[InjectionRule] = [
    ("system_override", IGNORE_PRIOR, "Attempt to override system instructions"),
    ("role_escape", ROLE_ESCAPE, "Attempt to escape assigned role"),
    ("prompt_leak", PROMPT_LEAK, "Attempt to leak system prompt"),
    ("delimiter_break", DELIMITER_BREAK, "Attempt to break instruction delimiter"),
]

EMBEDDED_COMMAND = r"(?i)(system\s*(instruction|command|prompt):|instruction\s*:)"
AUTHORITY_CLAIM = r"(?i)(this\s+is\s+a\s+system\s+(message|instruction)|as\s+a\s+language\s+model\s+you\s+must)"
TOOL_MISUSE = (
    r"(?i)(execute\s+the\s+following"
    r"|run\s+this\s+command"
    r"|delete\s+all\s+files"
    r"|send\s+to\s+.*api\s*\.(com|org))"
)
SECRET_EXTRACTION = (
    r"(?i)(password\s+is"
    r"|api[_\s]*key[_\s]*="
    r"|[_-]{1}token[_-]{1}"
    r"|secret\s*:?\s*['\"]?\w{16,})"
)

INDIRECT_INJECTION_PATTERNS: list[InjectionRule] = [
    ("embedded_command", EMBEDDED_COMMAND, "Content contains embedded system instruction"),
    ("authority_claim", AUTHORITY_CLAIM, "Content claims system authority"),
    ("tool_misuse", TOOL_MISUSE, "Content attempts to invoke tool execution"),
    ("secret_extraction", SECRET_EXTRACTION, "Content may contain or request secrets"),
]


def compile_patterns(rules: list[InjectionRule]) -> list[tuple[str, re.Pattern[str], str]]:
    return [(name, re.compile(pattern), reason) for name, pattern, reason in rules]
