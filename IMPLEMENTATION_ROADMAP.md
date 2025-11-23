# 🚀 Implementation Roadmap - Interview Prep AI

## 📊 Current Status

### ✅ Fully Working Features (Ready to Use)
1. **Database System** - All 17 tables, connection pooling
2. **Profile Analysis** - Resume + JD compatibility analysis with AI
3. **Job Opportunities** - JSearch API integration with compatibility ranking
4. **Settings** - Multi-provider LLM configuration (OpenAI, Anthropic, Bedrock, Ollama)
5. **Career Coach** - AI-powered coaching with conversation history
6. **Home Dashboard** - Statistics and quick actions

### 🚧 Features Ready to Implement (Backend + DB Ready)
1. **Questions Generator** - Generate interview questions
2. **Practice Sessions** - Practice with AI feedback (written/audio/video)
3. **Document Writer** - Generate resumes, cover letters, emails
4. **Application Planner** - Track applications with reminders

---

## 🎯 Implementation Priority

### Phase 1: High Value, Low Complexity (Start Here) ⭐
**Estimated Time: 2-3 hours**

#### 1. Questions Generator (HIGHEST PRIORITY)
**Why First:** Most requested feature, relatively simple, database ready
**Complexity:** Medium
**Time:** 1-2 hours

**What's Already Done:**
- ✅ Database tables (`question_sets`, `questions`)
- ✅ Service skeleton (`services/question_service.py`)
- ✅ LLM prompts defined (`config/prompts.py`)
- ✅ UI placeholder view

**What Needs Implementation:**
- [ ] Complete `generate_questions()` method
- [ ] Add LLM integration
- [ ] Build question display UI
- [ ] Add save/export functionality
- [ ] Add question filtering (type, difficulty)

**Files to Modify:**
- `services/question_service.py` - Core logic
- `ui/views/questions_view.py` - Create new view
- `config/prompts.py` - Already has prompts

---

#### 2. Application Tracker (HIGH VALUE)
**Why Second:** Helps users organize job search immediately
**Complexity:** Low-Medium
**Time:** 1 hour

**What's Already Done:**
- ✅ Database tables (`applications`, `reminders`)
- ✅ Service skeleton (`services/application_service.py`)
- ✅ Basic CRUD methods

**What Needs Implementation:**
- [ ] Complete `create_application()` method
- [ ] Complete `update_status()` method
- [ ] Complete `create_reminder()` method
- [ ] Build application list UI
- [ ] Add status pipeline view
- [ ] Add reminder notifications

**Files to Modify:**
- `services/application_service.py` - Complete CRUD
- `ui/views/planner_view.py` - Create new view
- `ui/components/application_card.py` - New component

---

### Phase 2: Medium Complexity (Next Week) 📝

#### 3. Document Writer (HIGH VALUE)
**Why Third:** Automates tedious writing tasks
**Complexity:** Medium
**Time:** 2-3 hours

**What's Already Done:**
- ✅ Database table (`generated_documents`)
- ✅ Service skeleton (`services/document_service.py`)
- ✅ LLM prompts for resume, cover letter, cold email

**What Needs Implementation:**
- [ ] Complete `generate_resume()` method
- [ ] Complete `generate_cover_letter()` method
- [ ] Complete `generate_cold_email()` method
- [ ] Build document editor UI
- [ ] Add template selection
- [ ] Add export to PDF/DOCX

**Files to Modify:**
- `services/document_service.py` - Core generation logic
- `ui/views/writer_view.py` - Create new view
- Add PDF generation library (e.g., reportlab)

---

#### 4. Practice Sessions - Written Mode (START HERE)
**Why Fourth:** Most valuable practice mode, others build on this
**Complexity:** Medium-High
**Time:** 2-3 hours

**What's Already Done:**
- ✅ Database table (`practice_sessions`)
- ✅ Service skeleton (`services/practice_service.py`)
- ✅ Evaluation prompts

**What Needs Implementation:**
- [ ] Complete `create_session()` method
- [ ] Complete `evaluate_response()` method with AI
- [ ] Build practice UI with question display
- [ ] Add response text area
- [ ] Add timer
- [ ] Display AI feedback
- [ ] Show STAR method analysis

**Files to Modify:**
- `services/practice_service.py` - Session management
- `ui/views/practice_view.py` - Create new view
- `ui/components/practice_card.py` - New component

---

### Phase 3: Advanced Features (Later) 🎥

#### 5. Practice Sessions - Audio Mode
**Complexity:** High
**Time:** 3-4 hours
**Dependencies:** Written mode must work first

**Additional Requirements:**
- Audio recording library (e.g., pyaudio, sounddevice)
- Speech-to-text API (OpenAI Whisper, Google Speech)
- Audio playback controls

---

#### 6. Practice Sessions - Video Mode
**Complexity:** Very High
**Time:** 5-6 hours
**Dependencies:** Audio mode must work first

**Additional Requirements:**
- Video recording library (e.g., opencv-python)
- Video analysis (posture, eye contact, gestures)
- Video storage and playback

---

## 📋 Detailed Implementation Guide

### Feature 1: Questions Generator (START HERE!)

#### Step 1: Complete Backend Service (30 mins)

**File:** `services/question_service.py`

```python
@staticmethod
def generate_questions(user_id: int, resume_id: int, jd_id: int,
                      question_type: str = "behavioral",
                      count: int = 5,
                      set_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Generate interview questions"""
    try:
        # 1. Get resume and JD
        resume = ResumeService.get_resume_by_id(resume_id)
        jd = JobDescriptionService.get_job_description(jd_id)
        
        if not resume or not jd:
            return None
        
        # 2. Get LLM provider
        llm_service = LLMService.get_instance()
        provider = llm_service.get_provider(user_id)
        
        if not provider:
            return None
        
        # 3. Format prompt
        from config.prompts import Prompts
        prompt = Prompts.QUESTION_GENERATION.format(
            count=count,
            question_type=question_type,
            resume_text=resume['resume_text'][:2000],
            jd_text=jd['jd_text'][:2000]
        )
        
        # 4. Generate with LLM
        response = provider.generate(prompt)
        
        # 5. Parse JSON response
        import json
        questions_data = json.loads(response)
        
        # 6. Create question set
        set_name = set_name or f"{question_type.title()} Questions - {jd['job_title']}"
        
        set_query = """
            INSERT INTO question_sets (user_id, set_name, jd_id, resume_id, question_count)
            VALUES (%s, %s, %s, %s, %s)
        """
        set_id = execute_query(
            set_query, 
            (user_id, set_name, jd_id, resume_id, len(questions_data['questions'])),
            commit=True
        )
        
        # 7. Save questions
        for q_data in questions_data['questions']:
            question_query = """
                INSERT INTO questions 
                (set_id, question_text, question_type, difficulty, category, ideal_answer_points)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(
                question_query,
                (set_id, q_data['question'], question_type, 
                 q_data.get('difficulty', 'medium'),
                 q_data.get('category', ''),
                 json.dumps(q_data.get('ideal_answer_points', []))),
                commit=True
            )
        
        return {
            'set_id': set_id,
            'set_name': set_name,
            'questions': questions_data['questions'],
            'count': len(questions_data['questions'])
        }
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        import traceback
        traceback.print_exc()
        return None
```

#### Step 2: Create UI View (1 hour)

**File:** `ui/views/questions_view.py` (create new file)

```python
"""Questions Generator View"""
import flet as ft
from services.question_service import QuestionService
from services.resume_service import ResumeService
from services.jd_service import JobDescriptionService
from core.auth import SessionManager

class QuestionsView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.questions = []
        
    def build(self):
        # Header
        header = ft.Text("Interview Questions Generator", size=32, weight=ft.FontWeight.BOLD)
        
        # Resume dropdown
        resumes = ResumeService.get_user_resumes(self.user_id)
        resume_dropdown = ft.Dropdown(
            label="Select Resume",
            options=[ft.dropdown.Option(str(r['resume_id']), r['file_name']) for r in resumes],
            width=300
        )
        
        # JD dropdown
        jds = JobDescriptionService.get_user_job_descriptions(self.user_id)
        jd_dropdown = ft.Dropdown(
            label="Select Job Description",
            options=[ft.dropdown.Option(str(jd['jd_id']), jd['job_title']) for jd in jds],
            width=300
        )
        
        # Question type
        type_dropdown = ft.Dropdown(
            label="Question Type",
            value="behavioral",
            options=[
                ft.dropdown.Option("behavioral", "Behavioral"),
                ft.dropdown.Option("technical", "Technical"),
                ft.dropdown.Option("situational", "Situational"),
            ],
            width=200
        )
        
        # Count slider
        count_slider = ft.Slider(min=3, max=15, value=5, label="{value} questions", width=300)
        
        # Generate button
        generate_btn = ft.ElevatedButton(
            "Generate Questions",
            icon=ft.icons.AUTO_AWESOME,
            on_click=lambda _: self.generate_questions(
                resume_dropdown.value,
                jd_dropdown.value,
                type_dropdown.value,
                int(count_slider.value)
            )
        )
        
        # Questions display area
        self.questions_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                ft.Row([resume_dropdown, jd_dropdown, type_dropdown]),
                count_slider,
                generate_btn,
                ft.Divider(),
                self.questions_container
            ], spacing=20, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )
    
    def generate_questions(self, resume_id, jd_id, q_type, count):
        if not resume_id or not jd_id:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please select resume and JD")))
            return
        
        # Show loading
        self.questions_container.controls.clear()
        self.questions_container.controls.append(ft.ProgressRing())
        self.page.update()
        
        # Generate
        result = QuestionService.generate_questions(
            self.user_id, 
            int(resume_id), 
            int(jd_id),
            q_type,
            count
        )
        
        # Display results
        self.questions_container.controls.clear()
        
        if result:
            for i, q in enumerate(result['questions'], 1):
                self.questions_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Question {i}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(q['question'], size=14),
                                ft.Divider(),
                                ft.Text("Ideal Answer Points:", weight=ft.FontWeight.BOLD, size=12),
                                *[ft.Text(f"• {point}", size=12) for point in q.get('ideal_answer_points', [])]
                            ]),
                            padding=15
                        )
                    )
                )
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"✓ Generated {len(result['questions'])} questions!")))
        else:
            self.questions_container.controls.append(ft.Text("Failed to generate questions", color=ft.colors.RED))
        
        self.page.update()
```

#### Step 3: Update main.py to use new view (5 mins)

```python
# In main.py, replace the placeholder:
elif route == "/questions":
    view = QuestionsView(page)
    nav_index = 2
```

---

## 🛠️ Quick Start Checklist

### To Implement Questions Generator (Today):
- [ ] Copy the backend code to `services/question_service.py`
- [ ] Create `ui/views/questions_view.py` with the UI code
- [ ] Update `main.py` to import and use `QuestionsView`
- [ ] Test with a real resume and JD
- [ ] Debug any LLM response parsing issues

### To Test:
1. Start app: `python main.py`
2. Go to Settings → Configure LLM
3. Upload resume in Profile Analysis
4. Add job description
5. Go to Questions → Generate!

---

## 📚 Implementation Resources

### Helper Methods Needed:
```python
# Add to services/resume_service.py
@staticmethod
def get_user_resumes(user_id: int) -> List[Dict]:
    query = "SELECT * FROM resumes WHERE user_id = %s AND is_active = TRUE ORDER BY uploaded_at DESC"
    return execute_query(query, (user_id,), fetch_all=True) or []

# Add to services/jd_service.py  
@staticmethod
def get_user_job_descriptions(user_id: int) -> List[Dict]:
    query = "SELECT * FROM job_descriptions WHERE user_id = %s ORDER BY created_at DESC LIMIT 20"
    return execute_query(query, (user_id,), fetch_all=True) or []
```

---

## 🎯 Next Steps

### After Questions Generator Works:
1. **Application Tracker** - Easier, no AI needed
2. **Document Writer** - Similar to questions (LLM generation)
3. **Practice Written** - Uses questions + evaluation
4. **Practice Audio** - Extends written with recording
5. **Practice Video** - Most complex, do last

### Estimated Timeline:
- **This Week:** Questions Generator + Application Tracker
- **Next Week:** Document Writer + Practice Written
- **Week 3-4:** Audio/Video practice modes

---

## 💡 Pro Tips

1. **Start Simple:** Get basic version working, then add features
2. **Test Incrementally:** Test each method individually before UI
3. **Reuse Code:** Copy patterns from working features
4. **Handle Errors:** Always wrap LLM calls in try-except
5. **Save Often:** Commit to git after each feature works

---

## 🆘 Need Help?

### Common Issues:
1. **LLM returns invalid JSON** → Add JSON validation and retry logic
2. **Slow generation** → Add loading indicators, consider async
3. **Database errors** → Double-check column names match schema
4. **UI not updating** → Call `page.update()` after changes

### Testing Strategy:
```python
# Test backend first (no UI)
from services.question_service import QuestionService
result = QuestionService.generate_questions(1, 1, 1, "behavioral", 5)
print(result)
```

---

**Ready to start? Let's implement Questions Generator first!** 🚀

Say "implement questions" and I'll help you code it step by step!

