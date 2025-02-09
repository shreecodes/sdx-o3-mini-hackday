import os
import openai
import json
from pathlib import Path

class ProjectManager:
    def __init__(self, project_dir):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.requirements_file = os.path.join(project_dir, "requirements.md")
        os.makedirs(os.path.dirname(self.requirements_file), exist_ok=True)

    def ask_clarifying_questions(self, initial_prompt):
        """Generate and ask clarifying questions based on the initial prompt."""
        messages = [
            {"role": "system", "content": """
You are an experienced project manager helping to scope web projects.
Ask 2-3 critical questions to better understand the project requirements. The user will also be able to free-form specify their answers.
Focus on questions that will significantly impact the project scope and direction.
Remember that the project will be a single-page webpage built with Next.js. Don't ask further about technical requirements or details.

Your response must be a JSON object with an array of question objects.
Example format:
{
    "questions": [
        {
            "question": "What is the primary target audience for this webpage?",
            "options": [
                "B2B",
                "Enterprise",
                "Government",
                "Non-profit"
            ]
        },
        {
            "question": "What is the main action you want visitors to take?",
            "options": [
                "Sign up for a newsletter",
                "Download a resource",
                "Book a demo"
            ]
        }
    ]
}
            """},
            {"role": "user", "content": f"Initial project idea: {initial_prompt}"}
        ]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={ "type": "json_object" }
        )

        questions_data = json.loads(response.choices[0].message.content)["questions"]
        answers = []

        print("\nTo better understand your needs, I have a few questions:\n")
        for i, q_data in enumerate(questions_data, 1):
            question = q_data["question"]
            options = q_data.get("options", [])
            
            print(f"{i}. {question}")
            if options:
                for j, option in enumerate(options):
                    print(f"\t{chr(97 + j)}. {option}")
            print()
            
            answer = input("Your answer: ").strip()
            answers.append({
                "question": question,
                "options": options,
                "answer": answer
            })

        return answers

    def generate_requirements(self, initial_prompt, qa_pairs):
        """Generate a structured requirements document based on the initial prompt and Q&A."""
        
        messages = [
            {"role": "system", "content": """
You are an experienced creative project manager creating requirements documents.
Based on the initial project idea and the clarifying questions, generate a clear creative vision for the project.
It should include the following sections:
1. Project Overview
2. Vibe and aesthetic of the project
3. Visual design guidelines
4. Key features and content sections
5. What the project should communicate

Leave out any technical details. Keep each section focused and concise. Use bullet points where appropriate.

Remember that the project will be a single-page webpage built with Next.js.
Don't include any technical details.

Begin your response with "1. Project Overview"
Do not reference 'your', speak professionally in the third person.
"""},
            {"role": "user", "content": f"""
            Initial Project Idea: {initial_prompt}
            
            Clarifying Q&A:
            {json.dumps(qa_pairs, indent=2)}
            """}
        ]

        response = self.openai_client.chat.completions.create(
            model="o3-mini",
            reasoning_effort="medium",
            messages=messages
        )

        return response.choices[0].message.content

    def save_requirements(self, project_name, requirements):
        """Save the requirements document to a file."""        
        with open(self.requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        return self.requirements_file

    def create_or_load_requirements(self):
        if os.path.exists(self.requirements_file):
            print(f"Loading requirements from {self.requirements_file}")
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return f.read(), True
        
        print("Welcome to the Project Requirements Generator!")
        print("Please describe your project idea (or type 'exit' to quit):")
        
        initial_prompt = input("\nProject idea: ").strip()

        # Get clarifying questions and answers
        qa_pairs = self.ask_clarifying_questions(initial_prompt)

        # Generate requirements document
        requirements = self.generate_requirements(initial_prompt, qa_pairs)

        # Save the requirements
        self.save_requirements(initial_prompt, requirements)
        return requirements, False


def main():
    pm = ProjectManager()
    pm.run()


if __name__ == "__main__":
    main()
