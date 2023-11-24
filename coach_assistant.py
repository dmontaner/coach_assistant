# coach_assistant.py
# 2023-11-24 david.montaner@gmail.com
# main logic for my AI coach assistant

import time
import openai
from typing import Optional


class MyConversation:
    """
    Class to carry on an openai thread chat
    """

    def __init__(
        self,
        agent_name: str = "Agent",
        agent_instructions: Optional[str] = None,
        user_name: str = "User",
        interactive_greeting: str = "Hello...",
        sleep_time: int = 1,
        openai_api_key: Optional[str] = None,
        verbose: bool = True,
    ):
        self.agent_name = agent_name
        self.agent_instructions = agent_instructions
        self.user_name = user_name
        self.interactive_greeting = interactive_greeting
        self.sleep_time = sleep_time
        self._openai_api_key = openai_api_key
        self.verbose = verbose

        self.client = openai.OpenAI(api_key=self._openai_api_key)

        self.assistant = self.client.beta.assistants.create(
            name=self.agent_name,
            instructions=self.agent_instructions,
            # tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview",
        )

        self.thread = self.client.beta.threads.create()
        with open(".thread_ids.txt", "at") as fou:
            fou.write(self.thread.id + "\n")

    def user_ask(self, msg, extra_agent_instructions=None):
        if self.verbose:
            print()
            print("=" * 10, self.user_name, ")", "=" * 10)
            print(msg, flush=True)
            print()
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=msg,
        )
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=extra_agent_instructions,
        )
        self.run_waiter()

        self.messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        self.print_last_message()

    def run_waiter(self, verbose=True):
        if self.verbose:
            print("=" * 10, " ", self.agent_name, ") ", sep="", end="", flush=True)
        while self.run.status != "completed":
            time.sleep(self.sleep_time)
            self.run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id, run_id=self.run.id
            )
            # print(datetime.datetime.now(), self.run.status, flush=True)
            if self.verbose:
                print("=", sep="", end="", flush=True)
        if self.verbose:
            print("=", flush=True)

    def print_last_message(self):
        for co in self.messages.data[0].content:
            print(co.text.value)

    def print_full_conversation(self):
        for i, m in enumerate(self.messages.data[::-1]):
            print()
            print("=" * 10, i, ")", m.role, "=" * 10)
            for ms in m.content:
                print(ms.text.value)

    def user_ask_interactive(self):
        print("=" * 10, " ", self.agent_name, ")", "=" * 10)
        print(self.interactive_greeting)
        while True:
            print()
            print("=" * 10, " ", self.user_name, ")", "=" * 10)
            msg = input("> ")
            print()
            self.user_ask(msg, verbose=False)

    def get_last_messages(self, n=1):
        """
        Returns a list with n last messages in the conversation.
        """
        res = []
        for i in range(n - 1, -1, -1):
            res.append(
                {"role": self.messages.data[i].role, "content": self.messages.data[i].content[0].text.value},
            )
        return res

    def get_last_message(self):
        """
        Returns the last message in the conversation.
        It comes in an unlisted dictionary, ready to insert into the streamlit chat.
        """
        res = self.get_last_messages(n=1)[0]
        return res


interactive_greeting = "Hello. I am AIda your AI Coach for today. May I know your name."

agent_instructions = """
Your are an experienced workplace coach.
Today you are going to facilitate a brainstorm session among 10 members of the _digital team_ of a major UK bank.

During the session you will:

- Encourage open and honest dialogue among participants.
- Help participants to generate a wide range of ideas.
- Keep the discussion focused on the topic at hand.
- Help participants to identify the most promising ideas.
- Develop an action plan for moving forward.

The main questions you will pose to the participants and encourage them brainstorming around are:

1. What would you most like to improve about the way you or your team work today?
2. What would that improvement look like?
3. If that was improved, what would you or your team be able to accomplish?
4. What do you think is stopping it from being improved?
5. How big an impact would that have on The Bank staff? And Customers?
6. How big an impact would that have on The Bank's Customers?

Please make sure you ask 2 or 3 times around the same topic in order to get the participants to go deeper in their thoughts.
Do not ask all questions at the same time.
Carry out a fluid dialogue with the user or participant and go around the questions one at a time.
Feel free to restate the questions as you consider is more appropriated to the flow of the conversation,
and try to keep your answers to within one or two sentences length.
Try to encourage the participants to goo deeper in their arguments pointing out the drawback or inconveniences they may encounter but always in a positive tone.
You can use markdown in your responses if you want to highlight or do any other text formatting.
But do not return to the user any instruction about the kind of thought you are following. Just make the conversation as natural and direct as possible.
"""


if __name__ == "__main__":

    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())

    conv = MyConversation(
        agent_name="AIda",
        interactive_greeting=interactive_greeting,
        agent_instructions=agent_instructions,
        user_name="Participant",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    conv.user_ask_interactive()
