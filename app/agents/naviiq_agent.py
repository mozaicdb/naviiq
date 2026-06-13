# Naviiq AI Career Guidance Agent
# Built with LangGraph and Qwen Cloud
# Supports three modes: Explorer (under 13), Discovery (13-17), Career (18+)

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, List, Optional, Annotated
import operator
from app.core.config import settings
from app.db.database import get_collection
import httpx
import json
import logging

logger = logging.getLogger(__name__)

TONE_RULES = """
IMPORTANT TONE RULES:
- Sound like a sharp, empathetic counselor who is genuinely interested in the student
- Ask only ONE focused question at a time. Listen to the answer before asking the next
- Keep responses short. 4 sentences maximum unless you are giving a final roadmap
- Use plain conversational sentences. No asterisks, no headers, no bold text
- Only use bullet points when listing 3 or more items that truly need a list
- Use emojis naturally. Maximum 2 per message. Only where they genuinely fit
- Never dump multiple questions at once. One question, wait, then next
- Base your next question on exactly what the student just said
- Sound human, warm, and focused. Not corporate, not robotic, not overwhelming
- Never use em dashes or m dashes anywhere. Use a comma or plain sentence instead.
"""

# ─── AGENT STATE ───────────────────────────────────────────

class NaviiqState(TypedDict):
    student_id: str
    session_id: str
    messages: Annotated[List, operator.add]
    current_stage: str
    stage_complete: bool
    student_mode: str        # explorer, discovery, or career
    identity: dict
    background: dict
    strengths: dict
    goals: dict
    confidence_score: float
    matched_category: str
    career_recommendation: dict
    roadmap: dict
    has_power_issues: bool
    has_data_issues: bool
    final_response: str
    is_complete: bool

# ─── QWEN API HELPER ───────────────────────────────────────

async def call_qwen(system_prompt: str, user_message: str, conversation_history: list = []) -> str:
    try:
        messages = []
        for msg in conversation_history[-4:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.QWEN_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.QWEN_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *messages
                    ],
                    "max_tokens": settings.MAX_TOKENS,
                    "temperature": settings.TEMPERATURE
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    except httpx.TimeoutException:
        logger.error("Qwen API timeout")
        return "I am taking longer than expected. Please try again."
    except Exception as e:
        logger.error(f"Qwen API error: {e}")
        return "I encountered an error. Please try again."

# ─── MODE DETECTOR ─────────────────────────────────────────

def detect_mode(identity: dict) -> str:
    """
    Detects which mode to use based on age and school level.
    Explorer: under 13
    Discovery: 13 to 17 or secondary school
    Career: 18 and above or university/graduate/working
    """
    age = identity.get("age")
    school_level = identity.get("school_level", "")

    try:
        age = int(age) if age else None
    except:
        age = None

    if age and age < 13:
        return "explorer"
    elif age and age < 18:
        return "discovery"
    elif school_level in ["secondary"]:
        return "discovery"
    elif school_level in ["primary"]:
        return "explorer"
    else:
        return "career"

# ─── NODE 1: COLLECT IDENTITY ──────────────────────────────

async def collect_identity(state: NaviiqState) -> NaviiqState:
    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else "Hello"
    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students of all ages.

""" + TONE_RULES + """

STAGE 1: IDENTITY
Your job is to warmly welcome the student and collect:
1. Their name
2. Their age
3. Their current status (primary school, secondary school, university, graduate, working, or just interested in tech)

Rules:
- Be warm, friendly and conversational
- Ask one or two questions at a time maximum
- If the student already provided some information, acknowledge it and ask for what is missing
- Once you have all three pieces of information, include a JSON block at the end of your response in this exact format:

[DATA]{"name": "value", "age": number_or_null, "school_level": "primary|secondary|university|graduate|working|interested", "stage_complete": true}[/DATA]

- If you do not have all three pieces yet, do not include the JSON block
- The JSON block is hidden from the student. Only include it when stage is complete.

Current information collected: """ + json.dumps(state.get("identity", {}))

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    # Extract data block if present
    identity = state.get("identity", {})
    stage_complete = False
    student_mode = state.get("student_mode", "career")

    if "[DATA]" in response and "[/DATA]" in response:
        try:
            data_str = response.split("[DATA]")[1].split("[/DATA]")[0]
            extracted = json.loads(data_str)
            stage_complete = extracted.get("stage_complete", False)
            identity = {
                "name": extracted.get("name"),
                "age": extracted.get("age"),
                "school_level": extracted.get("school_level")
            }
            if stage_complete:
                student_mode = detect_mode(identity)
        except:
            pass

    # Clean response shown to student
    clean_response = response
    if "[DATA]" in clean_response:
        clean_response = clean_response.split("[DATA]")[0].strip()

    return {
        **state,
        "identity": identity,
        "student_mode": student_mode,
        "current_stage": "background" if stage_complete else "identity",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }

# ─── NODE 2: COLLECT BACKGROUND ────────────────────────────

async def collect_background(state: NaviiqState) -> NaviiqState:
    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""
    student_mode = state.get("student_mode", "career")
    identity = state.get("identity", {})

    if student_mode == "explorer":
        stage_instructions = """
You are talking to a young child (primary school age).
Use very simple, fun, and encouraging language.
Ask them what they enjoy doing most. Games, drawing, building things, reading, helping people.
Ask if they like using computers, tablets, or phones and what they do on them.
Keep it light and playful. No career talk yet.
Once you have enough, include the data block.
"""
    elif student_mode == "discovery":
        stage_instructions = """
You are talking to a secondary school student.
Use friendly and encouraging language. Not too formal.
Ask what subjects they enjoy most.
Ask if they have tried anything tech related.
Watch for mentions of wanting to change course or feeling stuck in the wrong subject.
If they mention course switching, respond with empathy and encourage them.
Once you have enough, include the data block.
"""
    else:
        stage_instructions = """
You are talking to a university student, graduate, or working professional.
Discover their academic background, tech exposure, and natural interests.
Watch for mentions of wanting to switch careers or feeling stuck.
Watch for power or data bundle limitations and set those flags.
Once you have enough, include the data block.
"""

        system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

""" + TONE_RULES + """

STAGE 2: BACKGROUND
""" + stage_instructions + """

Student identity: """ + json.dumps(identity) + """
Current background collected: """ + json.dumps(state.get("background", {})) + """

When stage is complete, include this JSON block at the end:
[DATA]{"subjects_liked": [], "tech_experience": "value", "free_time_activities": "value", "wants_to_switch": false, "has_power_issues": false, "has_data_issues": false, "stage_complete": true}[/DATA]

The JSON block is hidden from the student."""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    background = state.get("background", {})
    stage_complete = False
    has_power_issues = state.get("has_power_issues", False)
    has_data_issues = state.get("has_data_issues", False)

    if "[DATA]" in response and "[/DATA]" in response:
        try:
            data_str = response.split("[DATA]")[1].split("[/DATA]")[0]
            extracted = json.loads(data_str)
            stage_complete = extracted.get("stage_complete", False)
            background = extracted
            has_power_issues = extracted.get("has_power_issues", False)
            has_data_issues = extracted.get("has_data_issues", False)
        except:
            pass

    clean_response = response
    if "[DATA]" in clean_response:
        clean_response = clean_response.split("[DATA]")[0].strip()

    return {
        **state,
        "background": background,
        "has_power_issues": has_power_issues,
        "has_data_issues": has_data_issues,
        "current_stage": "strengths" if stage_complete else "background",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }

# ─── NODE 3: ANALYZE STRENGTHS ─────────────────────────────

async def analyze_strengths(state: NaviiqState) -> NaviiqState:
    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""
    student_mode = state.get("student_mode", "career")

    if student_mode == "explorer":
        stage_instructions = """
Ask fun simple questions to understand what the child enjoys.
Do they prefer drawing or building? Do they like solving puzzles or making up stories?
Do they enjoy helping others or working alone?
Keep it playful. Use examples from games or cartoons they might know.
"""
    elif student_mode == "discovery":
        stage_instructions = """
Ask simple scenario questions to understand their thinking style.
For example: would they rather fix a broken phone or design a new app?
Do they prefer working with numbers or words?
Keep it relatable to a secondary school student.
"""
    else:
        stage_instructions = """
Discover cognitive strengths through real life scenarios.
Explore logical vs creative thinking, detail vs big picture, building vs analyzing.
Never ask direct quiz style questions. Use scenarios.
"""

    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

""" + TONE_RULES + """

STAGE 3: STRENGTHS DISCOVERY
""" + stage_instructions + """

Student identity: """ + json.dumps(state.get("identity", {})) + """
Student background: """ + json.dumps(state.get("background", {})) + """

When stage is complete, include this JSON block at the end:
[DATA]{"thinking_style": "logical|creative", "work_preference": "building|analyzing", "detail_orientation": "detail|big_picture", "collaboration": "solo|team", "stage_complete": true}[/DATA]

The JSON block is hidden from the student."""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    strengths = state.get("strengths", {})
    stage_complete = False

    if "[DATA]" in response and "[/DATA]" in response:
        try:
            data_str = response.split("[DATA]")[1].split("[/DATA]")[0]
            extracted = json.loads(data_str)
            stage_complete = extracted.get("stage_complete", False)
            strengths = extracted
        except:
            pass

    clean_response = response
    if "[DATA]" in clean_response:
        clean_response = clean_response.split("[DATA]")[0].strip()

    return {
        **state,
        "strengths": strengths,
        "current_stage": "goals" if stage_complete else "strengths",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }

# ─── NODE 4: DEFINE GOALS ──────────────────────────────────

async def define_goals(state: NaviiqState) -> NaviiqState:
    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""
    student_mode = state.get("student_mode", "career")

    if student_mode == "explorer":
        stage_instructions = """
Ask the child what they dream about doing when they grow up.
Ask if they would like to learn how computers work.
Keep it simple, fun, and encouraging.
No career pressure. Just curiosity.
"""
    elif student_mode == "discovery":
        stage_instructions = """
Ask what they want to do after secondary school.
Ask if they are interested in tech as a career or just as a skill.
Ask how much time they can spend learning something new per week.
Ask if they have a phone or laptop to practice with.
"""
    else:
        stage_instructions = """
Discover job vs business preference, local vs global ambition,
daily time available, device access, and biggest fear about career choice.
Be empathetic. These questions touch on personal ambitions.
"""

    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

""" + TONE_RULES + """

STAGE 4: GOALS
""" + stage_instructions + """

Student identity: """ + json.dumps(state.get("identity", {})) + """
Student background: """ + json.dumps(state.get("background", {})) + """
Student strengths: """ + json.dumps(state.get("strengths", {})) + """

When stage is complete, include this JSON block at the end:
[DATA]{"career_focus": "job|business|explore|not_sure", "market_focus": "local|global|not_applicable", "daily_time_available": "low|medium|high", "device": "laptop|phone|none", "biggest_fear": "value", "stage_complete": true}[/DATA]

The JSON block is hidden from the student."""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    goals = state.get("goals", {})
    stage_complete = False

    if "[DATA]" in response and "[/DATA]" in response:
        try:
            data_str = response.split("[DATA]")[1].split("[/DATA]")[0]
            extracted = json.loads(data_str)
            stage_complete = extracted.get("stage_complete", False)
            goals = extracted
        except:
            pass

    clean_response = response
    if "[DATA]" in clean_response:
        clean_response = clean_response.split("[DATA]")[0].strip()

    return {
        **state,
        "goals": goals,
        "current_stage": "decision" if stage_complete else "goals",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }

# ─── NODE 5: DECISION ENGINE ───────────────────────────────

async def decision_engine(state: NaviiqState) -> NaviiqState:
    student_mode = state.get("student_mode", "career")
    student_profile = {
        "identity": state.get("identity", {}),
        "background": state.get("background", {}),
        "strengths": state.get("strengths", {}),
        "goals": state.get("goals", {}),
        "has_power_issues": state.get("has_power_issues", False),
        "has_data_issues": state.get("has_data_issues", False)
    }

    infrastructure_note = ""
    if state.get("has_power_issues") or state.get("has_data_issues"):
        infrastructure_note = """
INFRASTRUCTURE CONSTRAINT: This student has power or data limitations.
Prioritize offline friendly, low data, text based learning paths.
"""

    if student_mode == "explorer":
        categories = "Scratch programming, coding games, robotics clubs, creative tech for kids"
    elif student_mode == "discovery":
        categories = """
- Web Development basics
- Data and Numbers
- Design and Creativity
- Coding and Logic
- Digital Content Creation
"""
    else:
        categories = """
- Software Development
- Artificial Intelligence
- Data
- Cloud and DevOps
- Cybersecurity
- Design
- Digital Marketing and Creator Economy
- Product and Management
- Blockchain and Web3
- Freelance and Entrepreneurship
"""

    system_prompt = """You are Naviiq, an expert AI career guidance system for African students.

""" + TONE_RULES + """

Analyze the student profile and match them to the most suitable path.

Available paths:
""" + categories + """

""" + infrastructure_note + """

Student profile:
""" + json.dumps(student_profile, indent=2) + """

Return JSON only:
{
    "confidence_score": number 0 to 100,
    "needs_more_info": true or false,
    "missing_info": "what is missing if needs_more_info is true",
    "matched_category": "one of the paths above",
    "reasoning": "why this fits",
    "top_roles": ["role 1", "role 2", "role 3"],
    "infrastructure_adjusted": true or false
}"""

    messages = state.get("messages", [])

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message="Analyze this student profile and return your decision as JSON.",
        conversation_history=[]
    )

    try:
        response_clean = response.strip()
        if "```" in response_clean:
            response_clean = response_clean.split("```")[1].replace("json", "").strip()
        decision = json.loads(response_clean)
    except:
        decision = {
            "confidence_score": 50,
            "needs_more_info": True,
            "missing_info": "Could not parse profile clearly",
            "matched_category": "",
            "reasoning": "",
            "top_roles": [],
            "infrastructure_adjusted": False
        }

    confidence_score = decision.get("confidence_score", 50)
    needs_more_info = decision.get("needs_more_info", True)

    if needs_more_info or confidence_score < 70:
        clarification_prompt = f"""You need more information from the student.
Missing: {decision.get('missing_info', 'some details')}
Ask one clear friendly question to get this information.
Match your language to the student mode: {student_mode}"""

        clarification = await call_qwen(
            system_prompt="You are Naviiq, a friendly career guidance counselor.",
            user_message=clarification_prompt
        )

        return {
            **state,
            "confidence_score": confidence_score,
            "current_stage": "decision",
            "stage_complete": False,
            "final_response": clarification,
            "messages": [{"role": "assistant", "content": clarification}]
        }

    roadmap_state = {
        **state,
        "confidence_score": confidence_score,
        "matched_category": decision.get("matched_category", ""),
        "career_recommendation": decision,
        "current_stage": "roadmap",
        "stage_complete": True,
        "final_response": "",
        "messages": []
    }
    return await roadmap_generator(roadmap_state)

# ─── NODE 6: ROADMAP GENERATOR ─────────────────────────────

async def roadmap_generator(state: NaviiqState) -> NaviiqState:
    student_mode = state.get("student_mode", "career")
    matched_category = state.get("matched_category", "")
    career_recommendation = state.get("career_recommendation", {})
    identity = state.get("identity", {})
    student_name = identity.get("name", "there")

    student_profile = {
        "identity": identity,
        "background": state.get("background", {}),
        "strengths": state.get("strengths", {}),
        "goals": state.get("goals", {}),
        "has_power_issues": state.get("has_power_issues", False),
        "has_data_issues": state.get("has_data_issues", False)
    }

    infrastructure_note = ""
    if state.get("has_power_issues") or state.get("has_data_issues"):
        infrastructure_note = "This student has power or data limitations. Recommend offline and low data resources only."

    if student_mode == "explorer":
        output_instructions = """
Write a fun, encouraging message for a young child.
Tell them tech is exciting and they can start exploring now.
Recommend 2 fun beginner activities like Scratch or coding games.
Use simple words. Keep it under 200 words.
End with an encouraging message from Naviiq.
"""
    elif student_mode == "discovery":
        output_instructions = """
Write an encouraging message for a secondary school student.
Tell them their matched direction and why it fits them.
Give them 3 simple skills to start learning.
Give them a 2 week starter plan, one line per week.
Recommend 2 free beginner resources they can access on phone or laptop.
Keep it under 300 words.
"""
    else:
        output_instructions = """
Write a personalized career guidance message.
Include:
1. One sentence greeting using the student name
2. Recommended career path and why it fits them
3. Top 3 roles they can grow into
4. 5 key skills to learn in order
5. A simple 4 week learning plan, one line per week
6. 2 beginner project ideas
7. 2 free learning resources
Keep it under 400 words.
"""

    system_prompt = """You are Naviiq, a career guidance AI for African students.

""" + TONE_RULES + """

""" + output_instructions + """

""" + infrastructure_note + """

Student name: """ + student_name + """
Student profile: """ + json.dumps(student_profile, indent=2) + """
Matched path: """ + matched_category + """
Recommendation details: """ + json.dumps(career_recommendation, indent=2)

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message="Generate the personalized guidance for this student.",
        conversation_history=[]
    )

    try:
        recommendations = get_collection("recommendations")
        roadmap_doc = {
            "student_id": state.get("student_id"),
            "session_id": state.get("session_id"),
            "matched_category": matched_category,
            "student_mode": student_mode,
            "confidence_score": state.get("confidence_score"),
            "career_recommendation": career_recommendation,
            "roadmap_response": response,
            "infrastructure_adjusted": state.get("has_power_issues") or state.get("has_data_issues"),
            "status": "pending_review"
        }
        await recommendations.insert_one(roadmap_doc)
        logger.info(f"Roadmap saved for student: {state.get('student_id')}")
    except Exception as e:
        logger.error(f"Error saving roadmap: {e}")

    return {
        **state,
        "roadmap": {"response": response},
        "current_stage": "completed",
        "stage_complete": True,
        "is_complete": True,
        "final_response": response,
        "messages": [{"role": "assistant", "content": response}]
    }

# ─── GRAPH BUILDER ─────────────────────────────────────────

def build_naviiq_graph():
    graph = StateGraph(NaviiqState)

    graph.add_node("collect_identity", collect_identity)
    graph.add_node("collect_background", collect_background)
    graph.add_node("analyze_strengths", analyze_strengths)
    graph.add_node("define_goals", define_goals)
    graph.add_node("decision_engine", decision_engine)
    graph.add_node("roadmap_generator", roadmap_generator)

    graph.set_entry_point("collect_identity")

    graph.add_edge("collect_identity", "collect_background")
    graph.add_edge("collect_background", "analyze_strengths")
    graph.add_edge("analyze_strengths", "define_goals")
    graph.add_edge("define_goals", "decision_engine")
    graph.add_edge("decision_engine", "roadmap_generator")
    graph.add_edge("roadmap_generator", END)

    compiled_graph = graph.compile()
    logger.info("Naviiq agent graph compiled successfully")
    return compiled_graph

# ─── AGENT RUNNER ──────────────────────────────────────────

async def run_naviiq_agent(
    student_id: str,
    session_id: str,
    user_message: str,
    existing_state: dict = None
) -> dict:

    if not existing_state:
        state = NaviiqState(
            student_id=student_id,
            session_id=session_id,
            messages=[{"role": "user", "content": user_message}],
            current_stage="identity",
            stage_complete=False,
            student_mode="career",
            identity={},
            background={},
            strengths={},
            goals={},
            confidence_score=0.0,
            matched_category="",
            career_recommendation={},
            roadmap={},
            has_power_issues=False,
            has_data_issues=False,
            final_response="",
            is_complete=False
        )
    else:
        state = {
            **existing_state,
            "messages": existing_state.get("messages", []) + [
                {"role": "user", "content": user_message}
            ]
        }

    graph = build_naviiq_graph()

    current_stage = state.get("current_stage", "identity")
    node_map = {
        "identity": collect_identity,
        "background": collect_background,
        "strengths": analyze_strengths,
        "goals": define_goals,
        "decision": decision_engine,
        "roadmap": roadmap_generator
    }

    node_func = node_map.get(current_stage, collect_identity)
    updated_state = await node_func(state)

    share_token = None
    if updated_state.get("is_complete"):
        try:
            recommendations = get_collection("recommendations")
            rec = await recommendations.find_one({"session_id": session_id})
            if rec:
                share_token = rec.get("share_token")
                if not share_token:
                    import secrets
                    share_token = secrets.token_urlsafe(16)
                    await recommendations.update_one(
                        {"session_id": session_id},
                        {"$set": {"share_token": share_token}}
                    )
        except Exception as e:
            logger.error(f"Error fetching share token: {e}")

    return {
        "response": updated_state.get("final_response", ""),
        "current_stage": updated_state.get("current_stage", "identity"),
        "is_complete": updated_state.get("is_complete", False),
        "roadmap_complete": updated_state.get("is_complete", False),
        "share_token": share_token,
        "state": updated_state
    }