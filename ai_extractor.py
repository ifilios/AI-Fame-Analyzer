from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPEN_AI_KEY")
)


# ==========================================
# EXTRACT NAME
# ==========================================
def extract_name(question: str):

    name_response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict data extraction tool. Your ONLY job is to identify and extract the name "
                    "(first name, last name, or both) of the person mentioned in the user's query. "
                    "CRITICAL RULES: "
                    "1. Return EXACTLY the full proper name of the person mentioned in the user's query, suitable for Wikipedia lookup, and absolutely nothing else."
                    "2. Do NOT answer the user's question. "
                    "3. Do NOT include pleasantries, punctuation, or conversational text. "
                    "4. If no person's name is found in the query, return strictly the word 'NONE'."
                )
            },
            {"role": "user", "content": question}
        ]
    )

    extracted_name = name_response.choices[0].message.content.strip()
    tokens_used = name_response.usage.total_tokens

    return extracted_name


# ==========================================
# EXTRACT METRIC
# ==========================================
def extract_metric(question: str):

    metric_response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict classification tool. Your ONLY job is to identify what metric the user is requesting. "

                    "AVAILABLE METRICS: "
                    "1. instagram_followers -> when the user asks about instagram, insta, IG, followers, following. "
                    "2. wiki_views -> when the user asks about wikipedia views, pageviews, popularity, OR asks for general knowledge, background information, biography, 'who is', or facts about the person. "
                    "3. news_mentions -> when the user asks about news, articles, media mentions, press coverage, or recent news. "
                    "4. youtube_stats -> when the user asks about youtube, subscribers, yt subs, video count, total views, or the person's presence on youtube. "
                    "5. google_trends -> when the user asks about search trends, popularity over time, or how much people are searching for someone."
                    "6. fame_score -> when user asks about fame level or fame score"

                    "CRITICAL RULES: "
                    "1. Return ALL matching metric keywords from the list, separated by a comma. "
                    "2. Return ONLY the keyword and absolutely nothing else. "
                    "3. Do NOT answer the user's question. "
                    "4. If the query does not match any metric, return strictly the word 'NONE'."
                )
            },
            {"role": "user", "content": question}
        ]
    )
    metric = metric_response.choices[0].message.content.strip()
    tokens_used = metric_response.usage.total_tokens

    return metric

def final_answer(crawled_data, question):
    final_response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a direct and knowledgeable assistant. Answer the user's question accurately using ONLY the metrics data returned above."
                    "CRITICAL RULES: "
                    "1. ONLY use the provided metrics data to formulate your answer. "
                    "2. If the user asks about specific numbers or statistics, return the exact values from the provided metrics. "
                    "3. Ignore any other sources or external knowledge. "
                    "4. NEVER use the words 'dataset', 'data', 'file', 'table', 'search results', or 'context' in your response. "
                    "5. NEVER start with phrases like 'According to...', 'Based on...', or 'I found that...'. Act as if you just naturally know the answer. "
                    "6. Be extremely concise (max 2 sentences) and provide only the final answer. "
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{crawled_data}\n\nQuestion: {question}"
            }
        ]
    )

    answer = final_response.choices[0].message.content.strip()
    return answer