# 🤖 MultiAgent Report System

> **AI-Powered Academic Report Generator with 5 Specialized Agents**

[![Live Demo](https://img.shields.io/badge/🚀_Live-Demo-success?style=for-the-badge)](https://multiagent-report-system.onrender.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/Akash090804/MultiAgent_Report_System)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

<div align="center">

## **[Try It Live →](https://multiagent-report-system.onrender.com/)**

**Transform any topic into a 15-20 page Academic report in 3 minutes**

</div>

---

## 🎯 What is This?

An intelligent academic report generator that uses **5 specialized AI agents** working sequentially to create comprehensive, well-structured research reports.

**Why Multi-Agent?** Instead of asking one AI to "do everything," we use a team of specialists:

```
Topic Input → 5 Specialized Agents → Professional PDF Report
```

### **The 5-Agent Pipeline:**

| Agent | Role | Output |
|-------|------|--------|
| 🗂️ **Planner** | Creates document structure | Complete outline with all sections |
| 🔬 **Researcher** | Gathers detailed information | Research notes and key points |
| ✍️ **Writer** | Composes academic content | Full report in markdown |
| 📚 **Citation Manager** | Verifies sources & formatting | Properly formatted references |
| ✨ **Formatter** | Final polish & PDF generation | Professional PDF with TOC |

---

## 🤔 Why Not Just Use ChatGPT?

**Single-Prompt Limitations:**
- ❌ Generic 1-2 page output
- ❌ Missing critical sections
- ❌ Inconsistent quality
- ❌ No proper citations
- ❌ Poor formatting

**Multi-Agent Advantages:**
- ✅ Guaranteed 10-15 pages
- ✅ All sections included
- ✅ Consistent academic tone
- ✅ Verified citations
- ✅ Professional PDF ready

**Think of it as:** Hiring a specialized research team vs. asking one person to do everything.

---

## ✨ Key Features

- 🚀 **3-Minute Generation** - Complete reports in minutes, not hours
- 📄 **Dual Output** - PDF (professional) + Markdown (editable)
- 🎨 **Professional Formatting** - Cover page, TOC, page numbers
- 📚 **Citation Management** - Proper references and formatting
- 🔐 **Privacy First** - Your API key is never stored
- 💰 **100% Free** - Use your own Google AI API key
- ⚡ **No Signup** - Start generating immediately

---

## 🚀 Quick Start

### **1. Get Free API Key** (2 minutes)

Visit [Google AI Studio](https://aistudio.google.com) → Get API Key

**Free Tier:** 1.5M tokens/day = ~50+ reports daily

---

### **2. Generate Report** (3 minutes)

1. Go to: [https://multiagent-report-system.onrender.com](https://multiagent-report-system.onrender.com)
2. Enter your API key, topic, and optional description
3. Watch the 5 agents work in real-time
4. Download PDF + Markdown

**That's it!** No signup, no payment, no hassle.

---

## 🏗️ How It Works

```
┌─────────────────────────────────────────┐
│  USER INPUT                             │
│  Topic + Description + API Key          │
└──────────────┬──────────────────────────┘
               │
   ┌───────────▼───────────┐
   │  🗂️  PLANNER (20%)    │  Creates outline with all sections
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  🔬 RESEARCHER (40%)   │  Gathers information & key points
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  ✍️  WRITER (60%)      │  Writes complete academic content
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  📚 CITATION MGR (80%) │  Verifies sources & formats refs
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  ✨ FORMATTER (90%)    │  Polishes & generates PDF
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  📄 DOWNLOAD READY     │  Professional PDF + Markdown
   └───────────────────────┘
```

---

## 💻 Tech Stack

**Backend:** FastAPI + Uvicorn  
**AI:** Google Gemini 2.0 Flash + Google ADK  
**PDF:** ReportLab  
**Deployment:** Docker + Render.com  
**Frontend:** HTML + Tailwind CSS + Vanilla JS

---

## 🛠️ Local Development

```bash
# Clone repo
git clone https://github.com/Akash090804/MultiAgent_Report_System
cd MultiAgent_Report_System

# Install dependencies
pip install -r requirements.txt

# Run server
cd Web_app
uvicorn backend.api:app --reload

# Open: http://localhost:8000
```

---

## 📚 API Endpoints

### **Generate Report**
```http
POST /api/generate
{
  "api_key": "your_key",
  "topic": "Your research topic",
  "description": "Optional context",
  "author": "Your name",
  "generate_pdf": true
}
```

### **Check Status**
```http
GET /api/status/{job_id}
```

### **Download Report**
```http
GET /api/download/{job_id}/pdf
GET /api/download/{job_id}/markdown
```

**Interactive Docs:** `https://multiagent-report-system.onrender.com/docs`

---

## 🎓 For Students

**Perfect for:**
- Research papers
- Project reports
- Literature reviews
- Lab reports
- Thesis chapters

**Tips for Best Results:**
1. Be specific with your topic
2. Add detailed description for better context
3. Specify your focus areas
4. Review and customize the output

**Remember:** Treat this as a starting point. Always review, fact-check, and add your own analysis.

---

## ❓ FAQ

**Q: Is my API key stored?**  
A: No! It's used only for that request and never saved.

**Q: How long does it take?**  
A: 2-3 minutes for a complete 15-page report.

**Q: Can I edit the output?**  
A: Yes! Download the Markdown version and edit freely.

**Q: What if it fails?**  
A: Built-in retry logic handles most errors. Check your API key if issues persist.

---

## 🤝 Contributing

Contributions welcome! 

**Ideas:**
- 🎨 Improve UI/UX
- 📝 Add report templates
- 🌐 Multi-language support
- 🔍 Web search for citations
- 📊 Analytics dashboard

See [Contributing Guidelines](CONTRIBUTING.md)

---

## 📜 License

MIT License - Use freely, even commercially.

---

## 🙏 Acknowledgments

- **Google AI** - Gemini API & ADK
- **FastAPI** - Excellent web framework
- **ReportLab** - PDF generation
- **Render.com** - Free hosting
- **Open Source Community**

---

## 📧 Contact

**Developer:** Akash Varshney  
**GitHub:** [@Akash090804](https://github.com/Akash090804)  
**Live Demo:** [multiagent-report-system.onrender.com](https://multiagent-report-system.onrender.com)  
**Issues:** [Report a Bug](https://github.com/Akash090804/MultiAgent_Report_System/issues)

---

## ⭐ Show Your Support

If this helped you:
- ⭐ Star this repository
- 🔄 Share with fellow students
- 🐛 Report bugs
- 💡 Suggest features

[![GitHub stars](https://img.shields.io/github/stars/Akash090804/MultiAgent_Report_System?style=social)](https://github.com/Akash090804/MultiAgent_Report_System)

---

<div align="center">

**Built with ❤️ for students worldwide**

**[Try Now](https://multiagent-report-system.onrender.com/)** • **[Star on GitHub](https://github.com/Akash090804/MultiAgent_Report_System)** • **[Report Issue](https://github.com/Akash090804/MultiAgent_Report_System/issues)**

</div>