from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

from b_agent_tools import vector_search, full_text_search


def get_llm_with_tools():
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o")
    # Create a chat prompt template for the agent, which includes a system prompt and a placeholder for `messages`
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "You are a helpful AI agent."
                " You are provided with tools to answer questions about tech companies earnings."
                " Think step-by-step and use these tools to get the information required to answer the user query."
                " Do not re-run tools unless absolutely necessary."
                " If you are not able to get enough information using the tools, reply with I DON'T KNOW."
                " You have access to the following tools: {tool_names}."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    tools = [vector_search, full_text_search]

    # Provide the tool names to the prompt
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    # Prepare the LLM by making the tools and prompt available to the model
    bind_tools = llm.bind_tools(tools)
    llm_with_tools = prompt | bind_tools
    return llm_with_tools


def get_tools() -> List[BaseTool]:
    """
    Get the tools available for the agent.
    """
    return [vector_search, full_text_search]


def main() -> None:
    agent = get_llm_with_tools()
    # Here, we expect the LLM to use the 'vector_search' tool.
    message = agent.invoke(
        ["What are the biggest challenges facing tech companies?"]
    ).tool_calls
    # Print the tool calls to see which tool was invoked
    print(message)

    # Here, we expect the LLM to use the 'full_text_search' tool.
    message = agent.invoke(
        ["find the document that mentions the largest driver of expense growth"]
    ).tool_calls
    print(message)


if __name__ == "__main__":
    main()
