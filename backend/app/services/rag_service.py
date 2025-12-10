from typing import List, Dict, TypedDict, Annotated
import logging
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# Removed agent imports that were causing issues
from fastapi import HTTPException
from app.core.constants import LLMConstants, VectorStoreConstants
from app.core.validation import validate_llm_model, validate_temperature, validate_top_k, validate_collection_name
import re
# Removed math tools for now, using enhanced prompts with OpenAI

logger = logging.getLogger(__name__)

class RAGState(TypedDict):
    """State for the RAG graph"""
    messages: Annotated[List[BaseMessage], "Chat messages history"]
    context: Annotated[List[Dict], "Retrieved document contexts"]
    question: Annotated[str, "User question"]
    answer: Annotated[str, "LLM generated answer"]
    llm_model: Annotated[str, "LLM model to use"]
    collection_name: Annotated[str, "Vector store collection name"]
    top_k: Annotated[int, "Number of documents to retrieve"]
    temperature: Annotated[float, "LLM temperature setting"]
    system_prompt: Annotated[str, "Custom system prompt"]
    custom_instructions: Annotated[str, "Custom instructions"]

class RAGService:
    """Service for Retrieval-Augmented Generation using LangGraph and LCEL"""
    
    def __init__(self, llm_service, vector_store_service):
        self.llm_service = llm_service
        self.vector_store_service = vector_store_service
        self._setup_graph()
    
    def _setup_graph(self):
        """Initialize the LangGraph workflow"""
        workflow = StateGraph(RAGState)
        
        # Define nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        
        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # Compile graph
        self.app = workflow.compile()
        
    async def _retrieve(self, state: RAGState) -> Dict:
        """Retrieve documents based on the last message"""
        try:
            question = state["messages"][-1].content
            collection_name = state["collection_name"]
            top_k = state.get("top_k", 5)
            
            vector_store = self.vector_store_service.create_collection_store(collection_name)
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )
            
            docs = await retriever.ainvoke(question)
            
            context = []
            for doc in docs:
                context.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
                
            return {"context": context, "question": question}
            
        except Exception as e:
            logger.error(f"Error in retrieve step: {e}")
            # Raise exception instead of silently continuing with empty context
            raise HTTPException(status_code=500, detail=f"Document retrieval failed: {str(e)}")

    async def _generate(self, state: RAGState) -> Dict:
        """Generate answer using LLM"""
        try:
            # Use dynamic default if not specified
            default_model = self.llm_service.get_primary_llm_type()
            llm_model = state.get("llm_model", default_model)
            temperature = state.get("temperature", 0.7)
            context = state["context"]
            messages = state["messages"]
            system_prompt = state.get("system_prompt", "")
            custom_instructions = state.get("custom_instructions", "")
            question = state["question"]

            # Check if this is a math question
            math_keywords = ['integral', 'derivative', 'calculate', 'solve', '∫', '∂', 'lim', 'sum', '∫', 'd/dx', 'dx', 'cos', 'sin', 'tan', 'log', 'ln', 'exp', 'sqrt', 'π', 'pi', 'alpha', 'beta', 'gamma', 'delta']
            is_math_question = any(keyword in question.lower() for keyword in math_keywords) or re.search(r'\$.*\$', question) or re.search(r'\\[a-zA-Z]+', question)

            if is_math_question:
                # For math questions, prefer OpenAI if available
                math_llm_model = "openai" if "openai" in self.llm_service.get_available_llms() else llm_model
                llm, _ = self.llm_service.get_llm(math_llm_model, temperature)

                # Format context string
                context_str = "\n\n".join([doc["content"] for doc in context])

                # Enhanced math system prompt
                math_system = """You are an expert mathematician and AI assistant. For mathematical questions:

1. Always solve problems step-by-step with correct calculations
2. Double-check your work at each step
3. Show all intermediate steps clearly
4. For integrals: show the antiderivative, then evaluate at bounds
5. For derivatives: show the differentiation rules used
6. Verify final answers make sense
7. Use proper mathematical notation
8. Be extremely careful with signs, limits, and algebraic manipulations

Use the provided context if relevant, but solve the math correctly regardless."""

                math_prompt = ChatPromptTemplate.from_messages([
                    ("system", math_system),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "Context: {context}\n\nQuestion: {question}\n\nSolve this mathematical problem step by step:")
                ])

                # Create chain
                chain = math_prompt | llm | StrOutputParser()

                # Prepare chat history
                chat_history = messages[:-1]

                response = await chain.ainvoke({
                    "context": context_str,
                    "chat_history": chat_history,
                    "question": question
                })

                return {"answer": response}
            else:
                # Regular LLM response
                # Get LLM
                llm, _ = self.llm_service.get_llm(llm_model, temperature)

                # Format context string
                context_str = "\n\n".join([doc["content"] for doc in context])

                # Create system message from session settings
                base_system = """You are a helpful AI assistant. Use the following context to answer the user's question.
If you don't know the answer based on the context provided, say so honestly. Don't make up information.

For mathematical questions, calculations, integrals, derivatives, or any math problems:
- Solve them step-by-step with correct calculations
- Double-check your math at each step
- Explain your reasoning clearly
- Show all intermediate steps
- Verify the final answer makes sense
- If it's an integral or derivative, clearly show the antiderivative/integral and evaluation at bounds
- Use proper mathematical notation and be extremely careful with signs, constants, and algebraic manipulations"""

                # Combine system prompt, custom instructions, and context
                full_system = base_system
                if system_prompt:
                    full_system = system_prompt
                if custom_instructions:
                    full_system += f"\n\nAdditional Instructions: {custom_instructions}"

                full_system += """

Context:
{context}
"""
                prompt = ChatPromptTemplate.from_messages([
                    ("system", full_system),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}")
                ])

                # Create chain
                chain = prompt | llm | StrOutputParser()

                # Prepare chat history (excluding the last message which is the current question)
                chat_history = messages[:-1]

                response = await chain.ainvoke({
                    "context": context_str,
                    "chat_history": chat_history,
                    "question": question
                })

                return {"answer": response}

        except Exception as e:
            logger.error(f"Error in generate step: {e}")
            raise

    async def chat(
        self,
        collection_name: str,
        message: str,
        chat_history: List[Dict],
        llm_model: str = None,  # Changed from default "ollama_cloud" to None
        temperature: float = LLMConstants.DEFAULT_TEMPERATURE,
        top_k: int = VectorStoreConstants.DEFAULT_TOP_K,
        system_prompt: str = None,
        custom_instructions: str = None
    ) -> Dict:
        """
        Chat with RAG using LangGraph
        """
        try:
            # Input validation
            if llm_model:
                llm_model = validate_llm_model(llm_model)
            temperature = validate_temperature(temperature)
            top_k = validate_top_k(top_k)
            collection_name = validate_collection_name(collection_name)

            # Resolve model if None
            if llm_model is None:
                llm_model = self.llm_service.get_primary_llm_type()

            # Convert chat history to LangChain format
            history_messages = []
            for msg in chat_history[-10:]:  # Keep last 10 messages
                if msg["role"] == "user":
                    history_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    history_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    history_messages.append(SystemMessage(content=msg["content"]))
            
            # Add current message
            history_messages.append(HumanMessage(content=message))
            
            # Invoke graph
            inputs = {
                "messages": history_messages,
                "collection_name": collection_name,
                "llm_model": llm_model,
                "temperature": temperature,
                "top_k": top_k,
                "system_prompt": system_prompt or "",
                "custom_instructions": custom_instructions or "",
                "context": [],
                "question": message,
                "answer": ""
            }
            
            result = await self.app.ainvoke(inputs)
            
            return {
                "answer": result["answer"],
                "sources": result["context"],
                "llm_used": llm_model
            }
            
        except Exception as e:
            logger.error(f"Error in chat with {llm_model}: {e}")
            
            # Fallback logic
            if llm_model == "ollama_cloud":
                fallback = "ollama_local"
            elif llm_model == "ollama_local":
                fallback = "openai"
            else:
                raise
                
            logger.info(f"Attempting fallback to {fallback}")
            return await self.chat(
                collection_name,
                message,
                chat_history,
                fallback,
                temperature,
                top_k,
                system_prompt,
                custom_instructions
            )

    async def simple_query(
        self,
        collection_name: str,
        query: str,
        llm_model: str = None,
        top_k: int = 5
    ) -> Dict:
        """Simple query wrapper"""
        return await self.chat(
            collection_name=collection_name,
            message=query,
            chat_history=[],
            llm_model=llm_model,
            top_k=top_k
        )
