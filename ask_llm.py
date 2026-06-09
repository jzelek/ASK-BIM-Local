import argparse
import sys

from local_llm_client import LocalLLMClient


def main():
    parser = argparse.ArgumentParser(
        description="Send one prompt directly to the local LLM."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Say ready.",
        help="The text to send to the local LLM.",
    )
    args = parser.parse_args()

    client = LocalLLMClient()

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": args.prompt,
                }
            ]
        )
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    print(response.choices[0].message.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
