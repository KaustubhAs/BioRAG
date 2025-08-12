class CLI:

    def __init__(self, rag_system):
        self.rag_system = rag_system

    def run(self):
        """Run the CLI interface."""
        print("Biomedical Assistant - Disease and Symptom Information")
        print("Type 'exit' to quit")

        while True:
            query = input("\nEnter your question: ")

            if query.lower() in ['exit', 'quit']:
                break

            response = self.rag_system.answer_query(query)
            print("\nResponse:")
            print(response)

        print("Thank you for using the Biomedical Assistant!")
