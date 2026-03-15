**Project Execution Instructions**

**1) Clone the repository**

```bash
git clone https://github.com/ifilios/AI-Fame-Analyzer.git
```

**2) Add the `.env` file to the project folder**
This file contains the necessary **API tokens** required for the application to function.

**3) Navigate to the project directory**

```bash
cd AI-Fame-Analyzer
```

**4) Build the Docker image**

```bash
docker build -t ai-fame-analyzer .
```

**5) Run the project**

```bash
docker run -p 9000:9000 ai-fame-analyzer
```

After running the container, you can access the application in your browser at:

```bash
http://localhost:9000
```

---

**Brief Overview of Our Application**

**AI Fame Analyzer** is a high-performance **automated celebrity intelligence system** that aggregates real-time popularity data from multiple online sources.
It combines **FastAPI**, data crawlers, and **OpenAI GPT-4o** to analyze the digital presence and influence of public figures.

The system collects data from **social media, search trends, knowledge bases, and news outlets** to generate a comprehensive **Fame Score (0-100)**.

---

### **Architecture**

The project follows a **three-layer architecture** designed for modularity, scalability, and clear separation of responsibilities.

#### 1. AI Extraction Layer (`ai_extractor.py`)

This layer uses AI to understand the user's request.

**Key Functions:**

* **Entity Extraction:** Uses GPT-4o to parse natural language queries and identify the celebrity name.
* **Intent Classification:** Determines which metrics should be retrieved (Instagram, YouTube, trends, etc.).

> This allows the system to dynamically fetch only the data needed for each request.

---

#### 2. Data Crawling Layer (`crawlers.py`)

Responsible for gathering **real-time data** from multiple external sources.

**Data Sources:**

* **Social Media:** Instagram follower counts via Serper / RapidAPI integrations.
* **Video Platforms:** YouTube subscriber counts and total views via the YouTube Data API v3.
* **Knowledge Base:** Wikipedia pageviews (last 60 days) and biography data through the MediaWiki API.
* **Market Interest:** Google Trends search velocity using the pytrends library.
* **Media Presence:** Global press mentions over the past 30 days via NewsAPI.

---

#### 3. Core Controller (`main.py`)

The controller orchestrates the interaction between the **AI extraction layer** and the **data crawlers**.

**Responsibilities:**

* Handling API requests through FastAPI
* Triggering the appropriate crawlers
* Aggregating collected data
* Computing the final **Fame Score**

---

### **Fame Score Algorithm**

The **Fame Score (0-100)** represents the overall **public visibility and influence** of a celebrity.

Because the collected metrics vary greatly in scale (e.g., millions of followers vs. hundreds of news articles), the algorithm uses **logarithmic normalization**:

```python
math.log10(value)
```

> This reduces extreme differences and ensures fair comparisons.

**Standard Weight Distribution**

| Metric              | Weight |
| ------------------- | ------ |
| Instagram Followers | 40%    |
| YouTube Subscribers | 25%    |
| Wikipedia Pageviews | 20%    |
| News Mentions       | 15%    |

**Dynamic Weighting:**
The system automatically adjusts the weight distribution when data is missing.

**Example:**
If a celebrity does not have a YouTube channel, the **25% YouTube weight** is redistributed proportionally among the remaining metrics.

> This prevents celebrities from receiving an artificially low **Fame Score** due to missing platforms
