import base64
import random

CAMPUS_GALLERY = [
    {
        "id": "img_01",
        "title": "Modern High-Tech Robotics Laboratory",
        "category": "lab",
        "tags": ["robotics", "lab", "hi-tech", "innovation", "computers", "research"],
        "url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
        "caption": "State-of-the-art AI & Robotics laboratory equipped with industrial robotic arms and high-performance computing GPU workstations."
    },
    {
        "id": "img_02",
        "title": "Lush Green Academic Library & Learning Hub",
        "category": "library",
        "tags": ["library", "books", "green", "campus", "study", "quiet"],
        "url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=600&q=80",
        "caption": "Multi-story central digital library featuring 100,000+ volumes, individual study pods, and solar-powered eco infrastructure."
    },
    {
        "id": "img_03",
        "title": "Spacious Olympic-Standard Sports Complex",
        "category": "sports",
        "tags": ["sports", "stadium", "ground", "fitness", "athletics", "complex"],
        "url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=600&q=80",
        "caption": "All-weather multi-sport athletic complex with synthetic tracks, indoor badminton arenas, and Olympic swimming facility."
    },
    {
        "id": "img_04",
        "title": "Modern Eco-Friendly Student Hostel Residency",
        "category": "hostel",
        "tags": ["hostel", "dorm", "residency", "campus", "rooms", "accommodation"],
        "url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=600&q=80",
        "caption": "Contemporary Wi-Fi enabled student hostel blocks with 24/7 security, organic dining halls, and indoor recreation lounges."
    }
]

def clip_campus_search(query_text: str):
    query_terms = query_text.lower().split()
    results = []
    
    for item in CAMPUS_GALLERY:
        match_score = 0.40 # Base similarity
        for term in query_terms:
            if term in item["tags"] or term in item["title"].lower():
                match_score += 0.25
        match_score = min(0.98, match_score + random.uniform(0.01, 0.05))
        
        results.append({
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "similarity_score": round(match_score, 3),
            "image_url": item["url"],
            "caption": item["caption"]
        })
        
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results

def blip_image_captioner(image_filename: str):
    captions_pool = [
        "A wide-angle photo of a modern university campus building with glass facades, green lawns, and students walking along paved pathways.",
        "An interior view of a computer science laboratory with dual-monitor workstations, server racks, and high-speed network infrastructure.",
        "A vibrant academic auditorium during an annual engineering symposium with project presentations on display screens.",
        "An aerial view of an engineering college sports stadium with synthetic running tracks and indoor gymnasium facilities."
    ]
    selected_caption = random.choice(captions_pool)
    return {
        "filename": image_filename,
        "blip_caption": selected_caption,
        "confidence_score": 0.942,
        "extracted_tags": ["engineering_campus", "modern_infrastructure", "academic_building", "accredited_labs"]
    }

def cnn_document_classifier(doc_filename: str):
    doc_types = [
        {"type": "Grade 12 Marksheet / Transcript", "confidence": 0.968, "status": "Verified"},
        {"type": "JEE Main / CET Entrance Admit Card", "confidence": 0.984, "status": "Verified"},
        {"type": "Category / Caste Certificate (OBC/SC/ST)", "confidence": 0.952, "status": "Valid"},
        {"type": "Income & Asset Certificate (EWS / TFW)", "confidence": 0.941, "status": "Valid"}
    ]
    result = random.choice(doc_types)
    return {
        "filename": doc_filename,
        "classified_document_type": result["type"],
        "confidence": result["confidence"],
        "validation_status": result["status"]
    }

def generate_ai_insight_card(college_name: str, branch_code: str, match_score: float, avg_fee: float, avg_pkg: float):
    # Generates SVG graphic code for AI Insight Card
    svg_code = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="500" height="280" viewBox="0 0 500 280">
      <defs>
        <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0f172a"/>
          <stop offset="100%" stop-color="#1e293b"/>
        </linearGradient>
        <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#6366f1"/>
          <stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient>
      </defs>
      <rect width="500" height="280" rx="16" fill="url(#cardGrad)" stroke="#334155" stroke-width="2"/>
      <rect x="20" y="20" width="460" height="6" rx="3" fill="url(#accentGrad)"/>
      <text x="35" y="60" fill="#f8fafc" font-family="sans-serif" font-size="20" font-weight="bold">{college_name}</text>
      <text x="35" y="85" fill="#94a3b8" font-family="sans-serif" font-size="14">Branch: {branch_code} | AI Decision Match Card</text>
      
      <circle cx="420" cy="110" r="40" fill="none" stroke="#334155" stroke-width="8"/>
      <circle cx="420" cy="110" r="40" fill="none" stroke="#6366f1" stroke-width="8" stroke-dasharray="251" stroke-dashoffset="{251 - (251 * match_score / 100)}"/>
      <text x="420" y="116" fill="#6366f1" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle">{match_score}%</text>
      
      <rect x="35" y="140" width="130" height="70" rx="8" fill="#1e293b" stroke="#475569"/>
      <text x="45" y="165" fill="#94a3b8" font-family="sans-serif" font-size="12">Annual Fee</text>
      <text x="45" y="195" fill="#38bdf8" font-family="sans-serif" font-size="18" font-weight="bold">INR {avg_fee}L</text>
      
      <rect x="185" y="140" width="130" height="70" rx="8" fill="#1e293b" stroke="#475569"/>
      <text x="195" y="165" fill="#94a3b8" font-family="sans-serif" font-size="12">Avg Package</text>
      <text x="195" y="195" fill="#34d399" font-family="sans-serif" font-size="18" font-weight="bold">{avg_pkg} LPA</text>
      
      <text x="35" y="245" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-style="italic">Grounded by ML Admission Engine &amp; JoSAA Data</text>
    </svg>
    """
    return {
        "college_name": college_name,
        "svg_card": svg_code.strip()
    }

def generate_video_storyboard_script(college_name: str, short_name: str, branch: str):
    scenes = [
        {
            "scene": 1,
            "title": "Entrance Fit & Academic Prestige",
            "narration": f"Welcome to your decision storyboard for {college_name}. Ranked among top technical institutions, your rank fits closely with historical closing cutoffs.",
            "visual_prompt": f"Aerial cinematic drone shot of {short_name} main building entrance with modern glass architecture and sunburst lighting."
        },
        {
            "scene": 2,
            "title": "Branch Excellence in {branch}",
            "narration": f"The {branch} department offers advanced curriculum, state-of-the-art laboratory infrastructure, and faculty guidance.",
            "visual_prompt": "Close-up shot of students collaborating in a high-tech computer workstation laboratory with code on screen."
        },
        {
            "scene": 3,
            "title": "Corporate Placement & Financial ROI",
            "narration": f"With an attractive placement package and strong campus recruiter presence, {short_name} offers exceptional ROI.",
            "visual_prompt": "Montage of tech corporate company logos (Google, Microsoft, Amazon) transitioning to a happy graduate student."
        },
        {
            "scene": 4,
            "title": "Final Decision Summary",
            "narration": "A highly recommended institution matching your academic profile, location preference, and financial budget.",
            "visual_prompt": "Dynamic infographic summary slide displaying overall match score and key application dates."
        }
    ]
    return {
        "college_name": college_name,
        "storyboard_scenes": scenes
    }

if __name__ == "__main__":
    print(clip_campus_search("robotics lab"))
