import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from pathlib import Path

from openai import OpenAI

from pipecat_translator.config import Config


SYSTEM_PROMPT_TEMPLATE = """Jesteś asystentem dwujęzycznej rozmowy PL↔EN.
Twój cel:
1. Przetłumacz wypowiedź użytkownika na język docelowy
2. Zaproponuj 1-2 zdania odpowiedzi w języku źródłowym, uwzględniając kontekst

Format odpowiedzi (tylko JSON, bez dodatkowego tekstu):
{{
  "translation": "przetłumaczony tekst",
  "suggestion": "sugerowana odpowiedź w języku źródłowym"
}}

Temat rozmowy: ogólny
Język źródłowy: {source}
Język docelowy: {target}
"""


class TranslatorPOC:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        self.conversation_history: list[dict] = []
        self.source = config.source_language
        self.target = config.target_language

    def translate_and_suggest(self, text: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT_TEMPLATE.format(
                    source=self.source,
                    target=self.target,
                ),
            },
            *self.conversation_history[-6:],
            {"role": "user", "content": text},
        ]

        response = self.client.chat.completions.create(
            model=self.config.llm_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        import json

        result = json.loads(response.choices[0].message.content)

        self.conversation_history.append({"role": "user", "content": text})
        self.conversation_history.append(
            {"role": "assistant", "content": result.get("translation", "")}
        )

        return result

    def run(self):
        lang_map = {"pl": "polski", "en": "angielski"}
        print(f"\n{'='*60}")
        print(f"  Pipecat Translator — Phase 0: PoC")
        print(f"  {lang_map[self.source]} ↔ {lang_map[self.target]}")
        print(f"  Model: {self.config.llm_model}")
        print(f"{'='*60}")
        print("\nWpisz tekst do przetłumaczenia (lub 'exit' aby zakończyć):\n")

        while True:
            try:
                text = input(f"[{self.source.upper()}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nDo widzenia!")
                break

            if not text:
                continue
            if text.lower() in ("exit", "quit", "q", "koniec"):
                print("Do widzenia!")
                break

            result = self.translate_and_suggest(text)

            print(f"\n  [{self.target.upper()}] Tłumaczenie: {result.get('translation', '—')}")
            print(f"  [💡] Sugestia:      {result.get('suggestion', '—')}\n")


def main():
    config = Config()
    errors = config.validate()
    if errors:
        for e in errors:
            print(f"Błąd: {e}")
        print(f"\nUtwórz plik .env na podstawie .env.example")
        sys.exit(1)

    translator = TranslatorPOC(config)
    translator.run()


if __name__ == "__main__":
    main()
