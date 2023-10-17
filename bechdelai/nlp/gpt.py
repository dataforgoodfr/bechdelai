import pandas as pd
import openai
from dotenv import load_dotenv
import os


class GPT3:
    def __init__(self,api_key = None):

        # Set up API key
        if api_key is None:
            try:
                load_dotenv()
                api_key = os.environ["OPENAI_API_KEY"]
            except:
                raise Exception("No OpenAI key was found in the environment or in a .env file")

        assert api_key.startswith("sk-")
        openai.api_key = api_key

    def generate(self,prompt,model = "text-davinci-003",max_tokens = 256,temperature = 0.7):

        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        try:
            return response["choices"][0]["text"]
        except:
            return response


    def make_prompt(self,question,dialogue):
        prompt = f"""
        Dialogue:
        {dialogue}
        -------------------------------
        You are a social scientist, feminist and expert in gender representation in cinema and in culture. 
        You know everything about the Bechdel test and study gender and ethnic inequalities, in particular how women are represented in movies and the stereotypes shown onscreen
        
        Please answer the following question about the dialogue above by detailing your reasoning

        Question: {question}
        Answer:
        """
        return prompt

    def answer_questions(self,questions,dialogue,**kwargs):

        if isinstance(questions,str): questions = [questions]

        answers = []

        for question in questions:
            prompt = self.make_prompt(question,dialogue)
            answer_question = self.generate(prompt,**kwargs)
            answers.append({"question":question,"answer":answer_question})
        answers = pd.DataFrame(answers)
        return answers