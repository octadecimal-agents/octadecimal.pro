import asyncio
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

from pipecat_translator.pipeline import run_console_session

load_dotenv()


def main():
    source_lang = sys.argv[1] if len(sys.argv) > 1 else "pl"
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "en"

    asyncio.run(run_console_session(source_lang, target_lang))


if __name__ == "__main__":
    main()
