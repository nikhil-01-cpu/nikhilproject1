import urllib.request, urllib.parse, json, re

ADZUNA_APP_ID  = "50e1fa18"
ADZUNA_API_KEY = "3ce258fe1e3a5709294916124f670c76"

FIELD_KEYWORDS = {
    "CSE/IT/Software":           "software developer intern",
    "AI/ML/Data Science":        "machine learning data science intern",
    "Civil/Mechanical/EEE":      "civil mechanical electrical engineering intern",
    "MBA/Marketing/Finance":     "marketing finance business development intern",
    "Design/UI-UX/Creative":     "UI UX graphic design intern",
    "Medical/Pharma/Healthcare": "pharma healthcare clinical research intern",
}

def detect_field(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ['cse','computer','software','it ','web','backend','frontend','java','python','react','node']):
        return 'CSE/IT/Software'
    if any(x in t for x in ['machine learning','ml','data science','ai ','nlp','deep learning','data analyst']):
        return 'AI/ML/Data Science'
    if any(x in t for x in ['civil','mechanical','eee','electrical','electronics','structural','autocad']):
        return 'Civil/Mechanical/EEE'
    if any(x in t for x in ['mba','marketing','finance','business','sales','hr ','human resource','consulting']):
        return 'MBA/Marketing/Finance'
    if any(x in t for x in ['design','ui','ux','graphic','figma','creative','animation']):
        return 'Design/UI-UX/Creative'
    if any(x in t for x in ['medical','pharma','health','biotech','clinical','mbbs','bpharma']):
        return 'Medical/Pharma/Healthcare'
    return 'CSE/IT/Software'

def get_logo(field):
    logos = {
        'CSE/IT/Software': '💻',
        'AI/ML/Data Science': '🧠',
        'Civil/Mechanical/EEE': '⚙️',
        'MBA/Marketing/Finance': '📊',
        'Design/UI-UX/Creative': '🎨',
        'Medical/Pharma/Healthcare': '🏥',
    }
    return logos.get(field, '🏢')

def fetch_live_internships(profile: dict, top_n: int = 15) -> list:
    education = profile.get('education', '')
    skills    = profile.get('skills', '')
    location  = profile.get('location', '')
    field     = detect_field(education + ' ' + skills)

    # Build smart search query
    base_keyword = FIELD_KEYWORDS.get(field, 'intern')
    # Add specific skills to search
    skill_list = [s.strip() for s in skills.split(',')][:2]
    if skill_list:
        keyword = f"{' '.join(skill_list)} intern"
    else:
        keyword = base_keyword

    results = []

    # Try India first, then worldwide
    countries = [('in', 'India'), ('gb', 'UK'), ('us', 'USA')]

    for country_code, country_name in countries:
        try:
            params = {
                'app_id':        ADZUNA_APP_ID,
                'app_key':       ADZUNA_API_KEY,
                'results_per_page': 10,
                'what':          keyword,
                'content-type':  'application/json',
                'sort_by':       'relevance',
            }
            # Add location if India
            if country_code == 'in' and location and location not in ['Any', '']:
                params['where'] = location

            url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'InternMatchAI/1.0'})
            res = urllib.request.urlopen(req, timeout=8)
            data = json.loads(res.read())

            for job in data.get('results', []):
                title = job.get('title', '')
                # Only internships
                if not any(x in title.lower() for x in ['intern', 'trainee', 'graduate', 'fresher', 'entry']):
                    if 'intern' not in job.get('description', '').lower()[:200]:
                        continue

                company  = job.get('company', {}).get('display_name', 'Company')
                location_raw = job.get('location', {}).get('display_name', country_name)
                salary_min = job.get('salary_min', 0)
                salary_max = job.get('salary_max', 0)
                apply_url  = job.get('redirect_url', '')
                description = job.get('description', '')

                # Stipend display
                if salary_min and salary_max:
                    stipend = int((salary_min + salary_max) / 2)
                elif salary_min:
                    stipend = int(salary_min)
                else:
                    stipend = 0

                # Match score
                match = calculate_match(profile, title, description)

                # Extract skills from description
                skills_found = extract_skills_from_desc(description)

                results.append({
                    "id":         str(job.get('id', '')),
                    "title":      title,
                    "company":    company,
                    "field":      field,
                    "location":   location_raw,
                    "stipend":    stipend,
                    "duration":   "3-6 months",
                    "skills":     skills_found,
                    "type":       "Industry",
                    "source":     "Adzuna",
                    "logo":       get_logo(field),
                    "apply_url":  apply_url,  # ✅ Direct apply link!
                    "matchScore": match,
                    "reasoning":  f"Live internship — {field}",
                    "description": description[:200] + '...' if len(description) > 200 else description,
                })

        except Exception as e:
            print(f"Adzuna error ({country_code}): {e}")
            continue

        if len(results) >= top_n:
            break

    # Sort by match score
    results.sort(key=lambda x: x['matchScore'], reverse=True)
    return results[:top_n]


def calculate_match(profile: dict, title: str, description: str) -> int:
    score = 45
    skills    = profile.get('skills', '').lower()
    education = profile.get('education', '').lower()
    text      = (title + ' ' + description).lower()

    for skill in skills.split(','):
        s = skill.strip()
        if s and len(s) > 2 and s in text:
            score += 10

    if any(x in education for x in ['cse', 'computer']) and any(x in text for x in ['software', 'developer']):
        score += 15
    if any(x in education for x in ['mba', 'bba']) and any(x in text for x in ['marketing', 'business', 'finance']):
        score += 15
    if 'intern' in title.lower():
        score += 10

    return min(score, 97)


def extract_skills_from_desc(description: str) -> list:
    common = ['Python','Java','JavaScript','React','Node.js','SQL','AWS','Excel',
              'Figma','AutoCAD','MATLAB','Marketing','Communication','Git',
              'TypeScript','C++','Docker','TensorFlow','Photoshop','Illustrator',
              'Power BI','Tableau','R','Django','Flask','Spring Boot','Kotlin','Swift']
    found = []
    desc_lower = description.lower()
    for skill in common:
        if skill.lower() in desc_lower:
            found.append(skill)
    return found[:5] if found else ['Communication', 'Problem Solving']
