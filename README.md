# GenAI Investment Advisor 📈
An AI-powered Stock Analyzer designed to assist retail investors with stock analysis. It retrieves real-time financial statements, historical price data, and news sentiment, using Large Language Models (LLMs) to generate detailed investment reports.

## 💡 Motivation
As a retail investor, if you do not have a finance background, understanding complex balance sheets, income statements, and financial metrics can be incredibly time-consuming and confusing. Most of us end up relying on finance content creators or random online forums to avoid manually processing this data. 
This project aims to solve that by building an AI-powered stock analysis assistant. It gathers real-time and historical data directly from financial APIs, aggregates recent market news sentiment, and uses LLMs to provide comprehensive, objective investment analysis.

## 🔬 Experimentation & Design Approaches
The bot utilizes several predefined functions and data collectors to gather stock information:
1. **Historical Stock Price Data**: Evaluates recent closing prices and volume trends (fetched via `yfinance`).
2. **Company Financial Statements**: Retrieves the last 3 years of balance sheet figures to evaluate financial health.
3. **Latest News**: Collects recent headlines from Google News RSS feed to capture real-time market sentiment.
### Comparison of Architectural Approaches
During development, two main architectures were tested:
#### 🧪 Approach 1: LangChain ReAct Agent
* **Mechanism**: Uses a Zero-Shot ReAct agent that dynamically reasons and selects which tool to run at runtime based on the user's prompt.
* **Findings**: Underperformed on complex financial questions. The agent frequently entered infinite loops of thoughts and actions or failed to reason accurately enough for complex investment decisions. 
* **Outcome**: Not recommended for production stability.
#### 🚀 Approach 2: Predefined Prompt with Function Calling (Current Implementation)
* **Mechanism**: Uses Llama-3.1 function calling via Groq to extract the target company name and its exact stock ticker (NSE format).
* **Findings**: Once the ticker is extracted reliably, the application fetches price history, balance sheets, and news in structured pipelines. The aggregate data is then analyzed by a high-performance Llama-3.3-70B model.
* **Outcome**: Highly stable, fast, and generates reliable reports. **This is the approach used in the application.**
---
## 📁 Project Structure
* **[app.py](app.py)**: The main entry point containing the Streamlit chat user interface and conversation history state management.
* **[tools/fetch_stock_info.py](tools/fetch_stock_info.py)**: Core utility module executing ticker extraction, web scraping, yfinance fetching, and LLM orchestration.
* **[stock_analyzer_bot.ipynb](stock_analyzer_bot.ipynb)**: Prototype development sandbox displaying raw API testing, function declarations, and intermediate outputs.
* **[requirements.txt](requirements.txt)**: List of Python packages required for the project.
* **[.env](.env)**: System environment variables configuration file (manages API keys).
---
## 🛠️ Installation & Setup
### 1. Clone or Open the Directory
Navigate to the project root directory:
```bash
cd genai-investment-advisor
```
### 2. Set Up a Virtual Environment (Recommended)
Create and activate a virtual environment to manage dependencies locally:
```bash
# Create virtual environment
python3 -m venv venv
#### Activate virtual environment
source venv/bin/activate
```
### 3. Install Dependencies
Install all required libraries specified in [requirements.txt](requirements.txt):
```bash
pip install -r requirements.txt
```
### 2. Configure API Key
Add your Gemini API Key in [tools/fetch_stock_info.py]

GEMINI_API_KEY = "your-api-key-here"
### 4. Configure Environment Variables
Create or update the `.env` file in the root directory:
```env
GROQ_API_KEY="your-groq-api-key-here"
```
### 3. Launch App
---
## 🖥️ Running the Application
### Launch Streamlit App
Run the Streamlit server from your terminal:
```bash
streamlit run app.py
```
This will automatically open a local web server (usually at `http://localhost:8501`) in your browser.
### Run Jupyter Notebook Playground
To run the prototype environment or run test cases cell-by-cell:
```bash
jupyter notebook stock_analyzer_bot.ipynb
```
---
## 💡 Example Queries
* "Should I invest in TCS?"
* "Evaluate the balance sheet health of Tata Motors."
* "Compare the working capital and overall liquidity of Infosys."
## 💡 Example Output
**Input Call:**
```python
Anazlyze_stock("Is it a good time to invest in Adani power?")
```
**Console/LLM Output:**
```json
{"Query": "Shall I invest in Adani power right now?", "Company_name": "Adani Power", "Ticker": "ADANIPOWER"}
```
```text
Analyzing.....
Investment Thesis for Adani Power:
1. Strong Financials: Adani Power has shown consistent growth in its financials over the past three years. The company has a positive tangible book value, indicating a strong asset base. Additionally, the company has a high invested capital, which suggests a strong financial position.
2. Increasing Stock Price: The stock price of Adani Power has been increasing steadily over the past few days. This indicates positive investor sentiment and potential for further growth in the future.
3. Declining Revenues: Adani Power has reported declining revenues in its recent quarterly results. This could be a concern for investors as it may indicate a slowdown in the company's business operations. However, further analysis is required to determine the reasons behind the decline and its potential impact on future performance.
4. Positive News Coverage: Adani Power has been in the news recently, with multiple articles highlighting the company's performance and prospects. Positive news coverage can attract more investors and potentially drive up the stock price.
5. Power Sector Outlook: The power sector in India is expected to grow in the coming years due to increasing demand for electricity. Adani Power, being a major player in the sector, is well-positioned to benefit from this growth. However, it is important to consider the competitive landscape and regulatory environment of the sector before making an investment decision.
Conclusion:
Based on the available data, investing in Adani Power right now could be a favorable option. The company has strong financials and a positive stock price trend. However, it is important to conduct further research and analysis to fully understand the reasons behind the declining revenues and assess the potential risks associated with the power sector.
```

## ⚠️ Disclaimer
> [!WARNING]
> This project is a hobby/learning application built for educational purposes. The creator is not a certified financial advisor. Always conduct your own research and consult with financial professionals before making actual investment decisions.
