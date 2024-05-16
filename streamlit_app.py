import streamlit as st
from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from Prompts import products_template_str
from CreateEmbedding import get_embedding
from pinecone import Pinecone, ServerlessSpec
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

# Load the environment variables from .env file
# dotenv.load_dotenv()



st.title('🔗 Amazon Products Agent')

openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

price_start_range = st.sidebar.slider('Price Start Range', 0, 200, 1, key="start_price")
price_end_range = st.sidebar.slider('Price End Range', 0, 200, 1, key="end_price")

category = st.sidebar.radio(label="Choose your product category", options = ("Office Accessories","Electronic Appliances"), key="category_val")
    









with st.form('my_form'):
    text = st.text_area('Enter your query:', key="question")

    submitted = st.form_submit_button('Submit')

    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')

    if submitted and openai_api_key.startswith('sk-'):
        question = st.session_state.question
        question_vector = get_embedding(question, openai_api_key)
        # Access the API keys
        if category == 'Office Accessories':
            pc = Pinecone(api_key=st.secrets['Office_Pine_Cone_API'])
            pinecone_client = pc.Index("amazon-fashion-products")
            results = pinecone_client.query(
                vector=question_vector,
                top_k=5,
                include_values=True,
                include_metadata=True,
                filter={
                    "price": {
                        "$gte": price_start_range,
                        "$lte": price_end_range
                    }
                }
            )
        else:
            pc = Pinecone(api_key=st.secrets['App_Pine_Cone_API'])
            pinecone_client = pc.Index("amazon-appliances")
            results = pinecone_client.query(
                vector=question_vector,
                top_k=5,
                include_values=True,
                include_metadata=True,
                filter={
                    "price": {
                        "$gte": price_start_range,
                        "$lte": price_end_range
                    }
                }
            )

        
        context =""

        # print(results.keys())
        for result in results['matches']:
            data = result['metadata']
            context += (
            f"title: {data['title']} "
            f"brand: {data['brand']} "
            f"description: {data['description']} "
            f"price: {data['price']} "
            f"ImageURL: {data['Image_URL']} \n\n"
            )

        products_system_prompt = SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["context"], template=products_template_str
                )
            )
        products_human_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["question"], template="{question}"
            )
        )
        messages = [products_system_prompt, products_human_prompt]
        products_prompt_template = ChatPromptTemplate(
            input_variables=["context", "question"],
            messages=messages,
        )
        # Format the messages
        formatted_messages = products_prompt_template.format_messages(context=context, question=question)
        
        # Initialize the chat model
        chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, openai_api_key = openai_api_key)
        output_parser = StrOutputParser()
        # Call the chat model with the formatted messages
        products_chain = products_prompt_template | chat_model | output_parser
        st.info(products_chain.invoke({"context": context, "question": question}))
        # Display the output
        
