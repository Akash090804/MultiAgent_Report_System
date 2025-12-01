# backend/generator.py
"""
Report generation logic integrated with the multi-agent system
This is the bridge between your existing agent.py and the web API
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.genai import errors as genai_errors

# Add parent directory to path to import from my_agent
project_root = Path(__file__).resolve().parent.parent.parent
my_agent_path = project_root / "my_agent"
sys.path.insert(0, str(project_root))  # Add Multiagent root
sys.path.insert(0, str(my_agent_path))  # Add my_agent directory
# Add virtual environment site-packages to path
venv_path = project_root / "agentvenv" / "Lib" / "site-packages"
if venv_path.exists():
    sys.path.insert(0, str(venv_path))
    print(f"[DEBUG] Added venv site-packages to path: {venv_path}")


print(f"[DEBUG] Python path includes: {my_agent_path}")
print(f"[DEBUG] Files in my_agent: {list(my_agent_path.glob('*.py')) if my_agent_path.exists() else 'Directory not found'}")


# Import your existing agents and PDF generator (lazy imports inside function)
rootagent = None
convert_markdown_to_pdf = None
extract_title_from_markdown = None

def _load_agent_modules():
    """Lazy load agent modules on first use"""
    global rootagent, convert_markdown_to_pdf, extract_title_from_markdown
    
    if rootagent is not None:
        return  # Already loaded
    
    try:
        from google.genai import types
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.genai import errors as genai_errors
        
        from my_agent import agent
        from my_agent import pdf_generator_simple
        rootagent = agent.rootagent
        convert_markdown_to_pdf = pdf_generator_simple.convert_markdown_to_pdf
        extract_title_from_markdown = pdf_generator_simple.extract_title_from_markdown
        print("[DEBUG] Successfully imported agent and pdf_generator from my_agent")
        return types, InMemorySessionService, Runner, genai_errors
    except ImportError as e:
        print(f"[ERROR] Could not import: {e}")
        print(f"[ERROR] Make sure agent.py and pdf_generator_simple.py exist in: {my_agent_path}")
        raise

APP_NAME = "web_report_generator"
USER_ID = "web_user"


async def run_report_generation(
    job_id: str,
    api_key: str,
    topic: str,
    description: str,
    author: str,
    generate_pdf: bool,
    jobs: dict
):
    """
    Run the complete report generation pipeline
    
    This function:
    1. Sets up the multi-agent pipeline
    2. Runs all 4 agents (Planner, Researcher, Writer, Formatter)
    3. Updates job status in real-time
    4. Generates PDF if requested
    5. Saves files to outputs/
    
    Args:
        job_id: Unique identifier for this job
        api_key: User's Google AI API key
        topic: Report topic
        description: Optional detailed description
        author: Optional author name
        generate_pdf: Whether to generate PDF
        jobs: Shared dictionary for status updates
    """
    
    print(f"\n[JOB {job_id}] Starting generation for topic: {topic}")
    
    try:
        # Ensure agent modules are loaded (rootagent is set)
        try:
            _load_agent_modules()
        except Exception as e:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = f"Failed to load agent modules: {e}"
            print(f"[JOB {job_id}] Failed to load agent modules: {e}")
            return

        # Set API key in environment
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Update status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 5
        jobs[job_id]["current_stage"] = "Setting up AI agents..."
        print(f"[JOB {job_id}] Setting up agents...")
        
        # Create pipeline with your existing rootagent
        pipeline = rootagent
        if pipeline is None:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Agent pipeline not loaded (rootagent is None)."
            print(f"[JOB {job_id}] ERROR: rootagent is None. Did imports fail?")
            return

        session_service = InMemorySessionService()

        try:
            runner = Runner(
                app_name=APP_NAME,
                agent=pipeline,
                session_service=session_service,
            )
        except Exception as e:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = f"Failed to create Runner: {e}"
            print(f"[JOB {job_id}] Failed to create Runner: {e}")
            return
        
        # Create unique session
        session_id = f"session_{job_id}"
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
        
        jobs[job_id]["progress"] = 10
        jobs[job_id]["current_stage"] = "Preparing prompt..."
        
        # Prepare full prompt (with optional description)
        if description:
            full_prompt = (
                f"Topic: {topic}\n\n"
                f"Detailed Context and Description:\n{description}\n\n"
                f"Please generate a comprehensive academic report based on the above topic and description. "
                f"Ensure all sections are relevant to the specific context provided."
            )
        else:
            full_prompt = topic
        
        print(f"[JOB {job_id}] Prompt prepared")
        
        # Create message
        user_message = types.Content(
            role='user',
            parts=[types.Part(text=full_prompt)]
        )
        
        # Agent progress tracking (5 agents with clear progress points)
        current_agent = None
        agent_progress = {
            'planner_agent': 20,
            'research_agent': 40,
            'writer_agent': 60,
            'formatter_agent': 80,
            'qc_agent': 90
        }
        
        agent_names = {
            'planner_agent': 'Planning structure',
            'research_agent': 'Researching content',
            'writer_agent': 'Writing report',
            'formatter_agent': 'Formatting document',
            'qc_agent': 'Quality check'
        }
        
        jobs[job_id]["progress"] = 15
        jobs[job_id]["current_stage"] = "Starting AI generation..."
        
        # Run pipeline with retry logic for model overload
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"[JOB {job_id}] Starting pipeline (attempt {attempt}/{max_attempts})")
                
                async for event in runner.run_async(
                    session_id=session_id,
                    user_id=USER_ID,
                    new_message=user_message,
                ):
                    # Track which agent is currently running
                    if hasattr(event, 'author'):
                        if event.author != current_agent:
                            current_agent = event.author
                            
                            if current_agent in agent_progress:
                                jobs[job_id]["progress"] = agent_progress[current_agent]
                                jobs[job_id]["current_stage"] = agent_names[current_agent]
                                print(f"[JOB {job_id}] Agent: {current_agent} ({agent_names[current_agent]})")
                
                # Success - break out of retry loop
                print(f"[JOB {job_id}] Pipeline completed successfully")
                break
                
            except genai_errors.ServerError as e:
                # Model overloaded (503 error)
                error_msg = str(e)
                print(f"[JOB {job_id}] ServerError on attempt {attempt}: {error_msg}")
                
                if attempt < max_attempts:
                    backoff = 2 ** attempt
                    jobs[job_id]["current_stage"] = f"Model busy, retrying in {backoff}s (attempt {attempt}/{max_attempts})..."
                    await asyncio.sleep(backoff)
                else:
                    raise Exception(f"Model overloaded after {max_attempts} attempts. Please try again later.")
            
            except genai_errors.ClientError as e:
                error_msg = str(e)
                print(f"[JOB {job_id}] ClientError: {error_msg}")
                
                # Handle specific client errors
                if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    jobs[job_id]["status"] = "failed"
                    jobs[job_id]["error"] = "API quota exceeded. Please check your API key limits or try again later."
                    return
                elif '401' in error_msg or 'UNAUTHENTICATED' in error_msg:
                    jobs[job_id]["status"] = "failed"
                    jobs[job_id]["error"] = "Invalid API key. Please check your Google AI API key."
                    return
                else:
                    raise
        
        # All agents completed, moving to PDF generation
        jobs[job_id]["progress"] = 95
        jobs[job_id]["current_stage"] = "Retrieving generated content..."
        print(f"[JOB {job_id}] Retrieving content from session...")
        
        # Get generated content from session state
        session = await session_service.get_session(
            session_id=session_id,
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        state = session.state
        
        # Try to get content from various possible keys
        final_md = (
            state.get("final_markdown", "") or 
            state.get("draft", "") or 
            state.get("research", "") or 
            state.get("outline", "")
        )
        
        if not final_md:
            print(f"[JOB {job_id}] ERROR: No content generated")
            print(f"[JOB {job_id}] Available state keys: {list(state.keys())}")
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No content was generated by the AI. Please try again."
            return
        
        print(f"[JOB {job_id}] Content retrieved: {len(final_md)} characters")
        
        # Ensure outputs directory exists (absolute path)
        outputs_dir = project_root / "Web_app" / "outputs"
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Save markdown file (absolute path)
        md_path = outputs_dir / f"report_{job_id}.md"
        with open(str(md_path), "w", encoding="utf-8") as f:
            f.write(final_md)
        
        print(f"[JOB {job_id}] Markdown saved: {md_path}")
        
        jobs[job_id]["progress"] = 90
        jobs[job_id]["markdown_url"] = f"/api/download/{job_id}/markdown"
        
        # Generate PDF if requested
        if generate_pdf:
            jobs[job_id]["current_stage"] = "Generating PDF..."
            print(f"[JOB {job_id}] Generating PDF...")
            
            try:
                # Extract title from markdown
                title = extract_title_from_markdown(final_md)
                
                metadata = {
                    "title": title,
                    "author": author or "AI Generated Report",
                    "date": datetime.now().strftime("%B %d, %Y")
                }
                
                pdf_path = outputs_dir / f"report_{job_id}.pdf"
                convert_markdown_to_pdf(final_md, str(pdf_path), metadata)
                
                print(f"[JOB {job_id}] PDF saved: {pdf_path}")
                jobs[job_id]["pdf_url"] = f"/api/download/{job_id}/pdf"
                
            except Exception as e:
                print(f"[JOB {job_id}] PDF generation failed: {e}")
                import traceback
                traceback.print_exc()
                jobs[job_id]["error"] = f"PDF generation failed: {str(e)}"
        
        # Mark as completed
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["current_stage"] = "Complete!"
        
        print(f"[JOB {job_id}]  Generation complete!")
        
    except Exception as e:
        print(f"[JOB {job_id}]  Error: {e}")
        import traceback
        traceback.print_exc()
        
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"] = 0