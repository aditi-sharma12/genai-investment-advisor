import json
import time
from bs4 import BeautifulSoup # type: ignore
import re
import requests
import yfinance as yf # type: ignore
import warnings
import os
from openai import OpenAI # type: ignore
from pydantic import BaseModel, Field # type: ignore
from langchain_openai import ChatOpenAI # type: ignore
from dotenv import load_dotenv # type: ignore

warnings.filterwarnings("ignore")

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

llm = ChatOpenAI(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
    openai_api_key=GROQ_API_KEY,
    openai_api_base="https://api.groq.com/openai/v1"
)

# Define structure for the model output
class CompanyStockTicker(BaseModel):
    company_name: str = Field(description="The name of the company given in query")
    ticker_symbol: str = Field(description="The stock ticker of the company without .NS suffix. E.g. RELIANCE, INFY")



# Fetch stock data from Yahoo Finance
def get_stock_price(ticker,history=5):
    try:
        if "." in ticker:
            ticker=ticker.split(".")[0]
        ticker=ticker+".NS"
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty:
            raise ValueError(f"No price data found for symbol: {ticker}")
        df=df[["Close","Volume"]]
        df.index=[str(x).split()[0] for x in list(df.index)]
        df.index.rename("Date",inplace=True)
        df=df[-history:]
        return df.to_string()
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        return "No stock price data available."




# Script to scrap top5 googgle news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    # url=f"https://www.google.com/search?q={search_term}&cr=countryIN"
    url=f"https://news.google.com/rss/search?q={search_term}&hl=en-IN&gl=IN&ceid=IN:en"
    url=re.sub(r"\s","+",url)
    return url



def get_recent_stock_news(company_name):
    try:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        g_query=google_query(company_name)
        res=requests.get(g_query,headers=headers).text
        soup=BeautifulSoup(res,"html.parser")
        news=[]
        for item in soup.find_all("item"):
            news.append(item.title.text)
        if len(news)>6:
            news=news[:4]
        else:
            news=news
        news_string=""
        for i,n in enumerate(news):
            news_string+=f"{i}. {n}\n"
        return "Recent News:\n\n"+news_string
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Recent News:\n\nCould not retrieve news headlines at this time."


# Fetch financial statements from Yahoo Finance
def get_financial_statements(ticker):
    try:
        if "." in ticker:
            ticker=ticker.split(".")[0]
        else:
            ticker=ticker
        ticker=ticker+".NS"    
        company = yf.Ticker(ticker)
        balance_sheet = company.balance_sheet
        if balance_sheet is None or balance_sheet.empty:
            raise ValueError(f"No balance sheet found for symbol: {ticker}")
        if balance_sheet.shape[1]>=3:
            balance_sheet=balance_sheet.iloc[:,:3]    # Remove 4th years data
        balance_sheet=balance_sheet.dropna(how="any")
        return balance_sheet.to_string()
    except Exception as e:
        print(f"Error fetching financial statements: {e}")
        return "No financial statement data available."



function=[
        {
        "name": "get_company_Stock_ticker",
        "description": "This will get the indian NSE/BSE stock ticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company.",
                },

                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given in query",
                }
            },
            "required": ["company_name","ticker_symbol"],
        },
    }
]

    
def get_stock_ticker(query):
    try:
        response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0,
                messages=[{
                    "role":"user",
                    "content":f"Given the user request, what is the comapany name and the company stock ticker ?: {query}?"
                }],
                functions=function,
                function_call={"name": "get_company_Stock_ticker"},
        )
        message = response.choices[0].message
        arguments = json.loads(message.function_call.arguments)
        company_name = arguments["company_name"]
        company_ticker = arguments["ticker_symbol"]
        return company_name, company_ticker
    except Exception as e:
        print(f"Error extracting ticker: {e}")
        return query, ""



def Anazlyze_stock(query):
    try:
        Company_name, ticker = get_stock_ticker(query)
        print({"Query": query, "Company_name": Company_name, "Ticker": ticker})   

        if not ticker or ticker.lower() == "none" or len(ticker.strip()) == 0:
            return f"Could not find a valid stock ticker for your query '{query}'. Please try asking about a specific company (e.g., 'Tata Motors' or 'Infosys')."
        stock_data = get_stock_price(ticker, history=10)
        stock_financials = get_financial_statements(ticker)
        stock_news = get_recent_stock_news(Company_name)

        if "No stock price" in stock_data and "No financial statement" in stock_financials:
            return f"Could not retrieve stock data or financials for ticker '{ticker}'. Please ensure the company is listed on the National Stock Exchange (NSE)."
        available_information = f"Stock Financials: {stock_financials}\n\nStock News: {stock_news}"
        print("\n\nAnalyzing.....\n")
        
        analysis = llm.invoke(f"Give detail stock analysis, Use the available data and provide investment recommendation. \
                 The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
                 User question: {query} \
                 You have the following information available about {Company_name}. Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination.Try to Give positives and negatives  : \
                  {available_information} "
                 ).content
        return analysis
    except Exception as e:
        print(f"Error in Anazlyze_stock execution: {e}")
        if "429" in str(e) or "rate_limit" in str(e).lower():
            return "Error: We are temporarily rate-limited by the AI provider. Please wait a few minutes and try again."
        return f"An error occurred during analysis: {str(e)}"
    

# Function to handle follow-up questions using the conversation history
def chat_follow_up(chat_history):
    try:
        response = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=chat_history,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in chat follow-up: {e}")
        return "Sorry, I encountered an error answering your follow-up query."

