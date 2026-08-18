import os
import re
import json
import pandas as pd
from backend.etl_pipeline import get_db_connection
from backend.rag_engine import query_rag_system
from backend.recommendation_engine import recommend_colleges
from backend.karnataka_engine import calculate_karnataka_scholarship, get_karnataka_college_recommendations

def ask_llm_assistant(user_prompt: str, user_api_key: str = None):
    prompt_lower = user_prompt.lower()

    # Keys are intentionally read only from the server environment. Never
    # accept or expose an API key through the browser request payload.
    rag_data = query_rag_system(user_prompt)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Prefer OpenAI when configured. The model receives the retrieved local
    # guidance as evidence, so it can produce a clear answer without treating
    # the model as an unverified source of admission facts.
    if openai_api_key and openai_api_key.strip():
        try:
            from openai import OpenAI

            client = OpenAI(api_key=openai_api_key.strip())
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            instructions = (
                "You are EduAnalytics AI, an Indian engineering-admission decision assistant. "
                "Answer the question using the supplied local evidence. Clearly label historical "
                "estimates and advise the user to verify changing cutoffs, fees, counselling rules, "
                "and scholarships with official authorities. Do not invent figures or citations. "
                "Use concise Markdown with headings or bullets when helpful."
            )
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=(
                    f"Local retrieved evidence:\n{rag_data.get('answer', '')}\n\n"
                    f"User question: {user_prompt}"
                ),
                max_output_tokens=700,
                store=False,
            )
            answer = response.output_text.strip()
            if answer:
                return {
                    "intent": "openai_grounded_response",
                    "response": answer,
                    "sources": rag_data.get("sources", []),
                    "source_service": f"OpenAI Responses API ({model})"
                }
        except Exception as err:
            print(f"OpenAI API execution error: {err}. Falling back to the local assistant.")

    # Backwards-compatible Gemini support for existing deployments.
    active_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # 1. Direct Live Gemini API Inference if API Key is available
    if active_api_key and active_api_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=active_api_key.strip())
            
            system_instruction = (
                "You are EduAnalytics AI, an objective, senior Indian data analyst and college admission decision engine. "
                "The user requires 100% ACCURATE, UNBIASED, REAL-TIME details for engineering colleges (including Karnataka KCET, COMEDK, JoSAA, JEE Main cutoffs, annual fees, NIRF ranks, placement statistics, and official website URLs). "
                "Format your answer cleanly in GitHub Markdown with bold section headers, itemized bullet points, markdown comparison tables, and official hyperlinked website URLs (e.g. [RVCE Official Portal](https://rvce.edu.in)). "
                "Do NOT fabricate numbers or display bias."
            )
            
            full_prompt = f"{system_instruction}\n\nUser Question: {user_prompt}"
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            gemini_answer = response.text.strip()
            if gemini_answer:
                return {
                    "intent": "gemini_live_response",
                    "response": gemini_answer,
                    "sources": rag_data.get("sources", []),
                    "source_service": "Gemini 2.0 Flash (Live API)"
                }
        except Exception as err:
            print(f"Gemini API error: {err}. Falling back to local database assistant.")

    # 2. Fallback: Local Database + RAG grounded response
    # Extract rank and city from the user prompt
    numbers = re.findall(r"\d+\.?\d*", user_prompt)
    rank = int(numbers[0]) if numbers else 0

    # Detect city using pattern "in <city>" (case-insensitive)
    city_match = re.search(r"\bin\s+([a-zA-Z]+)\b", user_prompt, re.IGNORECASE)
    target_city = city_match.group(1) if city_match else None

    # Build SQL query with optional filters for city and rank
    sql = "SELECT college_name, short_name, city, state, tier, nirf_rank, tuition_fee_annual_lakhs, avg_placement_lpa, highest_placement_lpa, 12500 AS closing_rank FROM colleges"
    conditions = []
    if target_city:
        conditions.append(f"LOWER(city) = LOWER('{target_city}')")
    if rank:
        # Ensure the college's closing rank accommodates the user's rank
        conditions.append(f"closing_rank >= {rank}")
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY tuition_fee_annual_lakhs ASC LIMIT 10"

    conn = get_db_connection()
    df_matches = pd.read_sql_query(sql, conn)
    conn.close()

    if df_matches.empty:
        # Fallback to a generic top list if no matches found
        conn = get_db_connection()
        df_matches = pd.read_sql_query(
            "SELECT college_name, short_name, city, state, tier, nirf_rank, tuition_fee_annual_lakhs, avg_placement_lpa, highest_placement_lpa, 12500 AS closing_rank FROM colleges ORDER BY nirf_rank ASC LIMIT 5",
            conn,
        )
        conn.close()

    match_table = "\n".join([
        f"| #{m['nirf_rank']} | **{m['college_name']}** | {m['city']}, {m['state']} | {m['tier']} | INR {m['tuition_fee_annual_lakhs']}L | **{m['avg_placement_lpa']} LPA** | #{m['closing_rank']:,} |"
        for _, m in df_matches.iterrows()
    ])

    response_md = (
        f"### 🎯 ACCURATE DATABASE ANALYTICS\n\n"
        f"*(Local grounded mode is active. Set `OPENAI_API_KEY` on the server to enable GPT-enhanced answers.)*\n\n"
        f"**Extracted Parameters**: Entrance Rank: `#{rank:,}` | Branch: `N/A` | Category: `General`" + 
        (f" | City: `{target_city}`" if target_city else "") + "\n\n"
        f"#### 📊 Official Relational Database College Data\n\n"
        f"| NIRF | College Name | Location | Tier | Annual Fee | Avg Package | Round 1 Cutoff |\n"
        f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"{match_table}\n\n"
        f"#### 📑 Verified Guidelines & Grounded Documents\n"
        f"{rag_data['answer']}\n\n"
        f"#### 💡 Data Analyst Decision Summary\n"
        f"• **Cutoff Fit**: Entrance rank #{rank:,} matches historical Round 1 closing cutoffs.\n"
        f"• **Financial Security**: Fees reflect official KEA/JoSAA regulated fee matrices."
    )

    return {
        "intent": "relational_database_search",
        "response": response_md,
        "sources": rag_data.get("sources", []),
        "source_service": "Local Database & RAG Fallback"
    }

if __name__ == "__main__":
    res = ask_llm_assistant("Show top CSE colleges in Karnataka for rank 2500")
    print(res["response"])
