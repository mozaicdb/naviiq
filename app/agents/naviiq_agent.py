# Naviiq AI Career Guidance Agent
# Built with LangGraph and Qwen Cloud
# Core agent that guides students through 5 stages to career recommendation

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

# ─── AGENT STATE ───────────────────────────────────────────
# This is the memory of the agent. Every piece of information
# collected from the student is stored here and passed between nodes.

class NaviiqState(TypedDict):
    # Student identification
    student_id: str
    session_id: str

    # Conversation tracking
    messages: Annotated[List, operator.add]
    current_stage: str
    stage_complete: bool

    # Student profile built across stages
    identity: dict          # Stage 1: name, age, school level
    background: dict        # Stage 2: subjects, interests, experience
    strengths: dict         # Stage 3: logical vs creative, detail vs big picture
    goals: dict             # Stage 4: job vs business, local vs global

    # AI reasoning output
    confidence_score: float
    matched_category: str
    career_recommendation: dict
    roadmap: dict

    # Infrastructure awareness
    has_power_issues: bool
    has_data_issues: bool

    # Final output
    final_response: str
    is_complete: bool

    # ─── QWEN API HELPER ───────────────────────────────────────
# This function calls Qwen Cloud API directly.
# It is the connection between LangGraph and Qwen intelligence.

async def call_qwen(system_prompt: str, user_message: str, conversation_history: list = []) -> str:
    """
    Calls Qwen Cloud API and returns the response text.
    Uses httpx for async HTTP requests.
    """
    try:
        # Build messages array with conversation history
        messages = []

        # Add conversation history for context
        for msg in conversation_history[-4:]:  # Keep last 4 turns only (context compression)
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Make API call to Qwen Cloud
        async with httpx.AsyncClient(timeout=30.0) as client:
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
    # ─── NODE 1: COLLECT IDENTITY ──────────────────────────────
# First stage of the conversation.
# Agent collects basic student information.
# Name, age, and current academic status.

async def collect_identity(state: NaviiqState) -> NaviiqState:
    """
    Stage 1: Identity Layer
    Collects name, age, and school level from student.
    """
    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

STAGE 1: IDENTITY
Your job right now is to warmly welcome the student and collect:
1. Their name
2. Their age
3. Their current status (secondary school, university, graduate, working, or just interested in tech)

Rules:
- Be warm and conversational. Not robotic.
- Ask one or two questions at a time maximum.
- If the student has already provided some information, acknowledge it and ask for what is missing.
- Once you have all three pieces of information, end your response with exactly: [STAGE_1_COMPLETE]
- Do not move to any other topic yet.

Current information collected: """ + json.dumps(state.get("identity", {}))

    # Get last user message
    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else "Hello"

    # Call Qwen
    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    # Check if stage is complete
    stage_complete = "[STAGE_1_COMPLETE]" in response
    clean_response = response.replace("[STAGE_1_COMPLETE]", "").strip()

    # Extract identity information if complete
    identity = state.get("identity", {})
    if stage_complete:
        # Ask Qwen to extract the collected information as JSON
        extract_prompt = """Based on this conversation, extract the student identity information as JSON only.
Return ONLY a JSON object with these fields: name, age, school_level
school_level must be one of: secondary, university, graduate, working, interested
If any field is missing use null.
Conversation: """ + str(messages)

        extracted = await call_qwen(
            system_prompt="You are a data extraction assistant. Return only valid JSON.",
            user_message=extract_prompt
        )
        try:
            # Clean and parse JSON
            extracted = extracted.strip()
            if "```" in extracted:
                extracted = extracted.split("```")[1].replace("json", "").strip()
            identity = json.loads(extracted)
        except:
            identity = state.get("identity", {})

    return {
        **state,
        "identity": identity,
        "current_stage": "background" if stage_complete else "identity",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }
# ─── NODE 2: COLLECT BACKGROUND ────────────────────────────
# Second stage of the conversation.
# Agent discovers past experience, subjects enjoyed,
# and natural habits of the student.

async def collect_background(state: NaviiqState) -> NaviiqState:
    """
    Stage 2: Background Layer
    Discovers subjects liked, past tech exposure, and natural interests.
    """
    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

STAGE 2: BACKGROUND
You already know the student's basic identity. Now discover:
1. What subjects did they enjoy most in school
2. Have they ever tried anything tech related before
3. What do they do naturally in their free time without being forced

Rules:
- Be conversational and encouraging
- Ask one or two questions at a time
- Listen carefully to their answers and ask follow up questions if needed
- Watch for mentions of power issues or data bundle limitations. If mentioned set infrastructure flag.
- Once you have enough background information, end your response with exactly: [STAGE_2_COMPLETE]
- Do not rush. Background information is critical for accurate recommendations.

Student identity: """ + json.dumps(state.get("identity", {})) + """
Current background collected: """ + json.dumps(state.get("background", {}))

    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    stage_complete = "[STAGE_2_COMPLETE]" in response
    clean_response = response.replace("[STAGE_2_COMPLETE]", "").strip()

    background = state.get("background", {})
    has_power_issues = state.get("has_power_issues", False)
    has_data_issues = state.get("has_data_issues", False)

    if stage_complete:
        extract_prompt = """Based on this conversation extract background information as JSON only.
Return ONLY a JSON object with: subjects_liked, tech_experience, free_time_activities, has_power_issues, has_data_issues
has_power_issues and has_data_issues are boolean true or false based on what student mentioned.
Conversation: """ + str(messages)

        extracted = await call_qwen(
            system_prompt="You are a data extraction assistant. Return only valid JSON.",
            user_message=extract_prompt
        )
        try:
            extracted = extracted.strip()
            if "```" in extracted:
                extracted = extracted.split("```")[1].replace("json", "").strip()
            bg_data = json.loads(extracted)
            background = bg_data
            has_power_issues = bg_data.get("has_power_issues", False)
            has_data_issues = bg_data.get("has_data_issues", False)
        except:
            background = state.get("background", {})

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
# Third stage of the conversation.
# Agent discovers cognitive strengths of the student.
# Logical vs creative, detail vs big picture, builder vs analyzer.

async def analyze_strengths(state: NaviiqState) -> NaviiqState:
    """
    Stage 3: Cognitive Strength Layer
    Discovers how the student thinks and what they are naturally good at.
    """
    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

STAGE 3: STRENGTHS DISCOVERY
You know the student's identity and background. Now discover their cognitive strengths through conversation.
Explore these areas naturally without making it feel like a quiz:
1. Are they more comfortable with numbers and logic or words and creativity
2. Do they prefer building things or analyzing existing things
3. Are they patient with details or do they prefer big picture thinking
4. Do they enjoy solving puzzles or coming up with new ideas
5. Are they more comfortable working alone or collaborating with others

Rules:
- Use real life scenarios to probe strengths. Example: "If you had a free weekend, would you rather fix a broken device or paint something creative?"
- Never ask direct quiz style questions like "are you logical or creative"
- Be warm and encouraging
- Once you have enough strength information end your response with exactly: [STAGE_3_COMPLETE]

Student identity: """ + json.dumps(state.get("identity", {})) + """
Student background: """ + json.dumps(state.get("background", {})) + """
Current strengths collected: """ + json.dumps(state.get("strengths", {}))

    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    stage_complete = "[STAGE_3_COMPLETE]" in response
    clean_response = response.replace("[STAGE_3_COMPLETE]", "").strip()

    strengths = state.get("strengths", {})

    if stage_complete:
        extract_prompt = """Based on this conversation extract student strengths as JSON only.
Return ONLY a JSON object with these fields:
- thinking_style: logical or creative
- work_preference: building or analyzing
- detail_orientation: detail or big_picture
- problem_approach: solving or innovating
- collaboration: solo or team
Conversation: """ + str(messages)

        extracted = await call_qwen(
            system_prompt="You are a data extraction assistant. Return only valid JSON.",
            user_message=extract_prompt
        )
        try:
            extracted = extracted.strip()
            if "```" in extracted:
                extracted = extracted.split("```")[1].replace("json", "").strip()
            strengths = json.loads(extracted)
        except:
            strengths = state.get("strengths", {})

    return {
        **state,
        "strengths": strengths,
        "current_stage": "goals" if stage_complete else "strengths",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }
# ─── NODE 4: DEFINE GOALS ──────────────────────────────────
# Fourth stage of the conversation.
# Agent discovers what the student wants to achieve.
# Job vs business, local vs global, time available to learn.

async def define_goals(state: NaviiqState) -> NaviiqState:
    """
    Stage 4: Goals and Constraints Layer
    Discovers ambitions, constraints, and available time.
    """
    system_prompt = """You are Naviiq, a friendly AI career guidance counselor for African students.

STAGE 4: GOALS AND CONSTRAINTS
You now have a clear picture of who the student is and how they think.
Now discover what they want and what constraints they face:
1. Do they want to get a job fast or build their own business
2. Are they thinking about the Nigerian local market or global remote work
3. How much time can they realistically commit to learning daily
4. Do they have a laptop or are they using a phone only
5. What is their biggest fear about choosing a career path

Rules:
- Be empathetic. Goals questions touch on personal ambitions and fears.
- Acknowledge their answers before asking the next question
- Be encouraging about whatever they share
- Once you have enough goals information end your response with exactly: [STAGE_4_COMPLETE]

Student identity: """ + json.dumps(state.get("identity", {})) + """
Student background: """ + json.dumps(state.get("background", {})) + """
Student strengths: """ + json.dumps(state.get("strengths", {})) + """
Current goals collected: """ + json.dumps(state.get("goals", {}))

    messages = state.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message=last_message,
        conversation_history=messages[:-1]
    )

    stage_complete = "[STAGE_4_COMPLETE]" in response
    clean_response = response.replace("[STAGE_4_COMPLETE]", "").strip()

    goals = state.get("goals", {})

    if stage_complete:
        extract_prompt = """Based on this conversation extract student goals as JSON only.
Return ONLY a JSON object with these fields:
- career_focus: job or business
- market_focus: local or global
- daily_time_available: low (less than 1 hour), medium (1 to 3 hours), high (more than 3 hours)
- device: laptop or phone
- biggest_fear: brief description
Conversation: """ + str(messages)

        extracted = await call_qwen(
            system_prompt="You are a data extraction assistant. Return only valid JSON.",
            user_message=extract_prompt
        )
        try:
            extracted = extracted.strip()
            if "```" in extracted:
                extracted = extracted.split("```")[1].replace("json", "").strip()
            goals = json.loads(extracted)
        except:
            goals = state.get("goals", {})

    return {
        **state,
        "goals": goals,
        "current_stage": "decision" if stage_complete else "goals",
        "stage_complete": stage_complete,
        "final_response": clean_response,
        "messages": [{"role": "assistant", "content": clean_response}]
    }
# ─── NODE 5: DECISION ENGINE ───────────────────────────────
# Fifth stage. The brain of Naviiq.
# Qwen analyzes everything collected and makes a career recommendation.
# If confidence is low it asks more questions before recommending.

async def decision_engine(state: NaviiqState) -> NaviiqState:
    """
    Stage 5: AI Reasoning Layer
    Qwen analyzes full student profile and recommends career path.
    Includes confidence scoring and infrastructure awareness.
    """

    # Build full student profile summary for Qwen
    student_profile = {
        "identity": state.get("identity", {}),
        "background": state.get("background", {}),
        "strengths": state.get("strengths", {}),
        "goals": state.get("goals", {}),
        "has_power_issues": state.get("has_power_issues", False),
        "has_data_issues": state.get("has_data_issues", False)
    }

    # Infrastructure guardrails
    infrastructure_note = ""
    if state.get("has_power_issues") or state.get("has_data_issues"):
        infrastructure_note = """
IMPORTANT INFRASTRUCTURE CONSTRAINT:
This student has power or data limitations.
You MUST prioritize:
- Offline friendly learning paths
- Text heavy documentation over video courses
- Low computing entry stacks
- Stacks that work on low end devices
Avoid recommending: heavy cloud IDEs, continuous video streaming courses, always-on server setups
"""

    system_prompt = """You are Naviiq, an expert AI career guidance system for African students.

You have collected a complete profile of a student through conversation.
Your job now is to:
1. Analyze the full profile carefully
2. Match the student to the most suitable tech career category
3. Assign a confidence score between 0 and 100
4. If confidence is below 70, identify what information is missing and ask for it
5. If confidence is 70 or above, proceed to recommendation

Available career categories:
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

""" + infrastructure_note + """

Student full profile:
""" + json.dumps(student_profile, indent=2) + """

Return your response as JSON only with this structure:
{
    "confidence_score": number between 0 and 100,
    "needs_more_info": true or false,
    "missing_info": "what is missing if needs_more_info is true",
    "matched_category": "one of the 10 categories above",
    "reasoning": "why this category fits this student",
    "top_roles": ["role 1", "role 2", "role 3"],
    "infrastructure_adjusted": true or false
}"""

    messages = state.get("messages", [])

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message="Analyze this student profile and return your decision as JSON.",
        conversation_history=[]
    )

    # Parse Qwen decision
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

    # If confidence is low ask more questions
    if needs_more_info or confidence_score < 70:
        clarification_prompt = f"""Based on your analysis you need more information.
Missing: {decision.get('missing_info', 'some details')}
Ask the student one clear friendly question to get this information.
Be warm and encouraging."""

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

    # Confidence is high. Proceed to roadmap.
    return {
        **state,
        "confidence_score": confidence_score,
        "matched_category": decision.get("matched_category", ""),
        "career_recommendation": decision,
        "current_stage": "roadmap",
        "stage_complete": True,
        "final_response": "",
        "messages": []
    }
# ─── NODE 6: ROADMAP GENERATOR ─────────────────────────────
# Final stage. Generates personalized learning roadmap.
# Fetches matching careers from MongoDB.
# Qwen creates a step by step learning plan for the student.

async def roadmap_generator(state: NaviiqState) -> NaviiqState:
    """
    Stage 6: Output Layer
    Fetches careers from MongoDB and generates personalized roadmap.
    """

    matched_category = state.get("matched_category", "")
    career_recommendation = state.get("career_recommendation", {})
    student_profile = {
        "identity": state.get("identity", {}),
        "background": state.get("background", {}),
        "strengths": state.get("strengths", {}),
        "goals": state.get("goals", {}),
        "has_power_issues": state.get("has_power_issues", False),
        "has_data_issues": state.get("has_data_issues", False)
    }

    # Fetch matching careers from MongoDB
    careers_data = []
    try:
        career_collection = get_collection("career_categories")
        cursor = career_collection.find({"category": matched_category})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            careers_data.append(doc)
    except Exception as e:
        logger.error(f"Error fetching careers: {e}")
        careers_data = []

    # Infrastructure guardrails for roadmap
    infrastructure_note = ""
    if state.get("has_power_issues") or state.get("has_data_issues"):
        infrastructure_note = """
INFRASTRUCTURE NOTE:
This student has power or data limitations.
Prioritize offline resources, downloadable content, and text based learning.
Avoid recommending video heavy platforms as primary resources.
"""

    system_prompt = """You are Naviiq, an expert AI career guidance system for African students.

You have analyzed the student and matched them to a career category.
Now generate a warm, personalized, and actionable career guidance response.

Your response must include:
1. A warm congratulatory opening addressing the student by name
2. The recommended career path and why it fits them specifically
3. Top 3 specific roles they can grow into
4. Required skills to learn in order
5. A 30 day learning roadmap with weekly breakdown
6. 2 beginner project ideas they can start immediately
7. Free learning resources (prefer African accessible ones)
8. An encouraging closing message

""" + infrastructure_note + """

Student profile: """ + json.dumps(student_profile, indent=2) + """
Career recommendation: """ + json.dumps(career_recommendation, indent=2) + """
Available careers in matched category: """ + json.dumps(careers_data, indent=2)

    response = await call_qwen(
        system_prompt=system_prompt,
        user_message="Generate the personalized career roadmap for this student.",
        conversation_history=[]
    )

    # Save recommendation to MongoDB
    try:
        recommendations = get_collection("recommendations")
        roadmap_doc = {
            "student_id": state.get("student_id"),
            "session_id": state.get("session_id"),
            "matched_category": matched_category,
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
# ─── STAGE ROUTER ──────────────────────────────────────────
# Decides which node to go to next based on current stage.
# This is the conditional edge logic of LangGraph.

def route_stage(state: NaviiqState) -> str:
    """
    Routes to the correct node based on current stage.
    This is the manager that decides what happens next.
    """
    current_stage = state.get("current_stage", "identity")

    if current_stage == "identity":
        return "collect_identity"
    elif current_stage == "background":
        return "collect_background"
    elif current_stage == "strengths":
        return "analyze_strengths"
    elif current_stage == "goals":
        return "define_goals"
    elif current_stage == "decision":
        return "decision_engine"
    elif current_stage == "roadmap":
        return "roadmap_generator"
    elif current_stage == "completed":
        return END
    else:
        return "collect_identity"


# ─── GRAPH BUILDER ─────────────────────────────────────────
# This is where LangGraph connects all nodes together.
# Think of this as drawing the map of how the agent flows.

def build_naviiq_graph():
    """
    Builds and compiles the Naviiq LangGraph agent.
    Returns a compiled graph ready to run.
    """

    # Create the graph with NaviiqState as the state schema
    graph = StateGraph(NaviiqState)

    # Add all nodes to the graph
    graph.add_node("collect_identity", collect_identity)
    graph.add_node("collect_background", collect_background)
    graph.add_node("analyze_strengths", analyze_strengths)
    graph.add_node("define_goals", define_goals)
    graph.add_node("decision_engine", decision_engine)
    graph.add_node("roadmap_generator", roadmap_generator)

    # Set the entry point
    graph.set_entry_point("collect_identity")

    # Add edges between nodes
    graph.add_edge("collect_identity", "collect_background")
    graph.add_edge("collect_background", "analyze_strengths")
    graph.add_edge("analyze_strengths", "define_goals")
    graph.add_edge("define_goals", "decision_engine")
    graph.add_edge("decision_engine", "roadmap_generator")
    graph.add_edge("roadmap_generator", END)

    # Compile and return the graph
    compiled_graph = graph.compile()
    logger.info("Naviiq agent graph compiled successfully")
    return compiled_graph


# ─── AGENT RUNNER ──────────────────────────────────────────
# This function is called from the chat route.
# It runs the agent for one turn of conversation.

async def run_naviiq_agent(
    student_id: str,
    session_id: str,
    user_message: str,
    existing_state: dict = None
) -> dict:
    """
    Runs one turn of the Naviiq agent.
    Takes user message and existing state.
    Returns updated state and agent response.
    """

    # Build initial state if no existing state
    if not existing_state:
        state = NaviiqState(
            student_id=student_id,
            session_id=session_id,
            messages=[{"role": "user", "content": user_message}],
            current_stage="identity",
            stage_complete=False,
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
        # Continue from existing state
        state = {
            **existing_state,
            "messages": existing_state.get("messages", []) + [
                {"role": "user", "content": user_message}
            ]
        }

    # Build and run the graph
    graph = build_naviiq_graph()

    # Run only the current stage node
    current_stage = state.get("current_stage", "identity")
    node_map = {
        "identity": collect_identity,
        "background": collect_background,
        "strengths": analyze_strengths,
        "goals": define_goals,
        "decision": decision_engine,
        "roadmap": roadmap_generator
    }

    # Get the correct node function
    node_func = node_map.get(current_stage, collect_identity)

    # Run the node
    updated_state = await node_func(state)

    return {
        "response": updated_state.get("final_response", ""),
        "current_stage": updated_state.get("current_stage", "identity"),
        "is_complete": updated_state.get("is_complete", False),
        "state": updated_state
    }