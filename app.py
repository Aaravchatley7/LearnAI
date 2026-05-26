import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

from models.pdf_reader import extract_text_from_pdf
from models.chapter_detector import detect_chapters
from models.summarizer import generate_summary
from models.topic_extractor import extract_topics
from models.mcq_generator import generate_mcqs
from models.llm import ask_groq
from models.performance_analyzer import get_all_performance

from database_utils.db import init_db
from database_utils.progress import save_progress, get_all_progress

from utils.helpers import allowed_file, score_color, score_emoji
from utils.prompts import TOPIC_EXPLANATION_SYSTEM, TOPIC_EXPLANATION_PROMPT

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

STORE = {
    "book_text":      "",
    "chapters":       {},
    "chapter_topics": {},
}


def _progress_records():
    """Return formatted progress rows for the dashboard."""
    records = []
    for r in get_all_progress():
        chapter, topic, score, total, timestamp = r
        pct = round((score / total * 100) if total > 0 else 0)
        records.append({
            "chapter": chapter, "topic": topic,
            "score": score, "total": total,
            "pct": pct, "color": score_color(pct),
            "timestamp": timestamp,
        })
    return records


# ── HOME (tabbed landing page) ─────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template(
        'index.html',
        chapters_list=list(STORE["chapters"].keys()),
        progress_records=_progress_records(),
        active_tab=request.args.get('tab', 'upload'),
    )


# ── UPLOAD ─────────────────────────────────────────────────────────────────────
@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return render_template('index.html', error="No file part in request.",
                               chapters_list=[], progress_records=_progress_records(),
                               active_tab='upload')

    file = request.files['pdf']
    if file.filename == '' or not allowed_file(file.filename):
        return render_template('index.html', error="Please upload a valid PDF file.",
                               chapters_list=[], progress_records=_progress_records(),
                               active_tab='upload')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    chapters = detect_chapters(text)

    STORE["book_text"] = text
    STORE["chapters"]  = chapters

    session['book_name'] = file.filename

    # Return to home with chapters tab open
    return render_template(
        'index.html',
        chapters_list=list(chapters.keys()),
        progress_records=_progress_records(),
        active_tab='chapters',
        upload_success=True,
    )
@app.route('/books/<path:book_path>')
def load_book(book_path):

    global STORE

    full_path = os.path.join('books', book_path)

    if not os.path.exists(full_path):

        return "Book not found"

    # Extract text from PDF
    text = extract_text_from_pdf(full_path)

    # Detect chapters
    chapters = detect_chapters(text)

    # Store data
    STORE['book_text'] = text
    STORE['chapters'] = chapters
    STORE['book_name'] = os.path.basename(book_path)

    # Store in session
    session['book_name'] = os.path.basename(book_path)

    return redirect('/?tab=chapters')

# ── STANDALONE CHAPTERS PAGE (from nav link) ───────────────────────────────────
@app.route('/chapters')
def chapters():
    if not STORE["chapters"]:
        return redirect(url_for('index'))
    return render_template('chapters.html',
                           chapters=list(STORE["chapters"].keys()),
                           book_name=session.get('book_name', 'Your Book'))


# ── CHAPTER SUMMARY ────────────────────────────────────────────────────────────
@app.route('/chapter/<path:chapter_name>')
def chapter(chapter_name):
    chapter_text = STORE["chapters"].get(chapter_name)
    if not chapter_text:
        return redirect(url_for('index'))

    summary = generate_summary(chapter_text)
    topics  = extract_topics(summary)

    STORE["chapter_topics"][chapter_name] = topics
    session['chapter_name'] = chapter_name
    session['topics']       = topics

    return render_template('summary.html',
                           chapter_name=chapter_name,
                           summary=summary,
                           topics=topics)


# ── TOPIC EXPLANATION + QUIZ ───────────────────────────────────────────────────
@app.route('/topic/<path:topic_name>')
def topic(topic_name):
    chapter_name = session.get('chapter_name', '')
    chapter_text = STORE["chapters"].get(chapter_name, "")

    prompt      = TOPIC_EXPLANATION_PROMPT.format(topic=topic_name)
    explanation = ask_groq(prompt, system=TOPIC_EXPLANATION_SYSTEM, temperature=0.6, max_tokens=600)
    mcqs        = generate_mcqs(topic_name, chapter_context=chapter_text, count=4)

    topics      = session.get('topics', [])
    current_idx = topics.index(topic_name) if topic_name in topics else 0
    next_topic  = topics[current_idx + 1] if current_idx + 1 < len(topics) else None
    progress_percent = int(((current_idx + 1) / len(topics)) * 100) if topics else 0

    return render_template('quiz.html',
                           topic=topic_name,
                           explanation=explanation,
                           mcqs=mcqs,
                           chapter_name=chapter_name,
                           topics=topics,
                           current_idx=current_idx,
                           next_topic=next_topic,
                           progress_percent=progress_percent)


# ── QUIZ SUBMISSION ────────────────────────────────────────────────────────────
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    chapter_name = session.get('chapter_name', 'Unknown')
    topic_name   = request.form.get('topic_name', 'Unknown')
    total        = int(request.form.get('total_questions', 0))
    next_topic   = request.form.get('next_topic', '')

    score   = 0
    results = []
    for i in range(total):
        user_ans    = request.form.get(f'q{i}', '')
        correct_ans = request.form.get(f'correct{i}', '')
        question    = request.form.get(f'question{i}', '')
        is_correct  = (user_ans == correct_ans)
        if is_correct:
            score += 1
        results.append({"question": question, "user_answer": user_ans,
                        "correct_answer": correct_ans, "is_correct": is_correct})

    save_progress(chapter=chapter_name, topic=topic_name, score=score, total=total)
    pct = round((score / total * 100) if total > 0 else 0)

    return render_template('result.html',
                           score=score, total=total, pct=pct,
                           results=results,
                           topic_name=topic_name,
                           chapter_name=chapter_name,
                           next_topic=next_topic,
                           score_color=score_color(pct),
                           score_emoji=score_emoji(pct))


# ── PROGRESS (standalone page) ─────────────────────────────────────────────────
@app.route('/progress')
def progress():
    return render_template('progress.html', records=_progress_records())


# ── RUN ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
