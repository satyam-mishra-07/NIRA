from providers.llm.openrouter_provider import (
    chat_with_nira
)


def main():

    print("\nNIRA is online.")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if not user_input.strip():
            continue

        if user_input.lower() == "exit":

            print("\nNIRA: See you later, Satyam.\n")
            break

        try:

            response = chat_with_nira(user_input)

            print(f"\nNIRA: {response}\n")

        except Exception as error:

            print(f"\n[ERROR]: {error}\n")


if __name__ == "__main__":
    main()