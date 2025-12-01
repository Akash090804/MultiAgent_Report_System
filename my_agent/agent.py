from google.adk.agents import LlmAgent,SequentialAgent
import os
from dotenv import load_dotenv
from google.genai import types
from google.adk.tools import google_search


API_KEY = os.getenv("GOOGLE_API_KEY")
# Planner: generates a numbered markdown outline and stores it in state['outline']
PlannerAgent = LlmAgent(
    name="planner_agent",
    model="gemini-2.5-flash",
    
    instruction=(
        "You are the Planner Agent. Given a project topic string in the user message, "
        "produce a numbered Markdown outline for an academic/project report that includes the following sections:\n\n"
        "- Declaration\n"
        "- Certificate\n"
        "- Acknowledgement\n"
        "- Abstract\n"
        "- Table of Contents\n"
        "- Introduction\n"
        "- Literature Review\n"
        "- Research Design and Methodology\n"
        "- Results and Discussion\n"
        "- Conclusion and Future Scope\n"
        "- References\n\n"
        "Return only the Markdown outline. Make section headings clear and numbered."
    ),
    output_key="outline"
)

# 2. RESEARCH AGENT: expands each section of the outline with detailed content
ResearchAgent = LlmAgent(
    name="research_agent",
    model="gemini-2.5-flash",
    
    instruction=(
        "You are the Research Agent. Based on the topic and any outline provided above, "
        "produce detailed research notes and key points for each section. "
        "Do not repeat the outline. Do not write full paragraphs yet.\n"
        "For each section provide 8-10 key points and suggest 4-5 short citation placeholders like [1], [2].\n\n"
        "Save the result as a Markdown document suitable for feeding into a writer."
    ),
    output_key="research",
    tools=[google_search]
)


# 3. WRITER AGENT: composes the full report using the outline and research notes
WriterAgent = LlmAgent(
    name="writer_agent",
    model="gemini-2.5-flash",  
    
    instruction=(
        "You are the Writer Agent. Using the research material and topic provided above, "
        "write a full academic-style report in Markdown. Use bold headings for sections (e.g. **1. Introduction**). "
        "Include placeholders for Declaration, Certificate, and Acknowledgement, and ensure each section is reasonably sized. "
        "IMPORTANT: Write each section ONCE only. Do NOT repeat sections. "
        "Do NOT add code fences. "
        "Make sure to include references section at the end with citation placeholders."
        "You can use multiple paragraphs and bullet points to improve readability."
    ),
    output_key="draft"
)


# 4. Formatter AGENT: formats the draft into a polished final report
FormatterAgent = LlmAgent(
    name="formatter_agent",
    model="gemini-2.5-flash",  
    
    instruction=(
        "You are the Formatter Agent. Take the draft content provided above and: "
        "1) Remove ANY duplicate sections or repeated content "
        "2) Ensure bold headings are consistent and numbered (1., 1.1, ...)\n"
        "3) Insert a Table of Contents at the top with links to sections (Markdown style)\n"
        "4) Make spacing and line breaks consistent\n"
        "5) Fix any formatting issues\n\n"
        "Return the polished Markdown as the final output."
    ),
    output_key="formatted"
)

# 5. QUALITY CHECK & CITATION AGENT: removes repetition, cleans formatting, ensures proper structure
QCAgent = LlmAgent(
    name="qc_agent",
    model="gemini-2.5-flash",
    
    instruction=(
        "You are the Quality Control and Citation Agent. Review the document provided above and:\n\n"
        "TITLE FORMATTING:\n"
        "1) If the main title/heading at top is very long (>60 chars), break it into title + subtitle\n"
        "2) Separate title and subtitle with one blank line\n"
        "3) Ensure title is clear and professional\n\n"
        "REPETITION CHECK:\n"
        "4) Identify and REMOVE any repeated sentences, paragraphs, or entire sections\n"
        "5) Keep only the first occurrence of repeated content\n"
        "6) Ensure no topic appears more than once\n\n"
        "FORMATTING CLEANUP:\n"
        "7) Remove any stray ** or ## symbols that are not part of proper headings\n"
        "8) Fix markdown formatting: use # for main sections, ## for subsections, ### for sub-subsections\n"
        "9) Ensure bold text (**text**) is only used where intentional\n"
        "10) Remove extra blank lines (keep max 1 blank line between sections)\n\n"
        "TABLE OF CONTENTS FORMATTING:\n"
        "11) Format the Table of Contents with proper indentation and structure:\n"
        "    # Table of Contents\n"
        "    - Main Sections (no indent)\n"
        "      - Subsections (2-space indent)\n"
        "        - Sub-subsections (4-space indent)\n"
        "12) Use simple hyphens (-) for bullets, no other symbols or Unicode characters\n"
        "13) Keep TOC concise and aligned, remove duplicate entries\n"
        "14) Make sure all sections in TOC actually exist in the document\n\n"
        "STRUCTURE & SPACING:\n"
        "15) Add a page break indicator (---) between MAJOR sections ONLY (not subsections)\n"
        "16) Place --- on its own line with blank lines before and after\n"
        "17) Ensure at least one blank line after major section headings before content\n"
        "18) Keep Table of Contents right after document title/author information\n"
        "19) Ensure References section is at the very end\n\n"
        "CONTENT QUALITY:\n"
        "20) Verify all citations [1], [2], etc. are valid and referenced in References section\n"
        "21) Remove verbose/redundant descriptions - keep content concise and professional\n"
        "22) Ensure each section is substantive but not repetitive\n"
        "23) Ensure section headings are clear but not excessively long (max 80 characters)\n\n"
        "Return the cleaned, final-ready Markdown document. This is the final output for PDF generation."
    ),
    output_key="final_markdown"
)


rootagent = SequentialAgent(
    name="root_agent",
    sub_agents=[PlannerAgent, ResearchAgent, WriterAgent, FormatterAgent, QCAgent]
)