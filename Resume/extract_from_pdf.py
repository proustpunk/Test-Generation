import re
from .models import Job
from .utils import handle_pdf


class DescriptionHandler:
    """
    Extracts structured fields from IT job description PDFs or text files.

    Handles 20+ structural format variations found across job boards (LinkedIn,
    Indeed, Dice, Greenhouse, Lever, Workday, government portals, staffing agencies).

    Extracted fields: job_title, experience, salary, location, body
    """

    # ------------------------------------------------------------------ #
    #  TITLE patterns                                                       #
    # ------------------------------------------------------------------ #
    # Ordered from most-specific to least-specific to avoid false positives.
    _TITLE_PATTERNS = [
        # Format 4/13/16 — bracketed or ALL-CAPS label
        # [Job Title]: Cloud Engineer  |  JOB TITLE: ...  |  POSITION TITLE: ...
        re.compile(
            r'^\s*\[?(?:Job\s*Title|Position\s*Title|Position|Role|Title)\]?\s*[:\-\.]+\s*(.+)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Format 10 — bold markdown  **Position:** Senior Engineer
        re.compile(
            r'\*{1,2}(?:Job\s*Title|Position|Role|Title)\*{1,2}\s*[:\-]\s*(.+)',
            re.IGNORECASE
        ),
        # Format 6 — pipe-delimited first segment  "Senior QA Engineer | Remote | ..."
        # Only match if it looks like a title (no sentence punctuation, ≤ 80 chars)
        re.compile(
            r'^([A-Z][^\n|]{3,79}?)\s*\|',
            re.MULTILINE
        ),
        # Format 1/7/11 — bare first non-empty line that looks like a job title
        # Must start with capital, no colon, short enough to be a title
        re.compile(
            r'^\s*(?:We(?:\'re|\s+are)\s+(?:Hiring|Looking\s+For)[:\s]+)?'
            r'([A-Z][A-Za-z0-9 /&\-\(\)–,]{2,80}?)\s*$',
            re.MULTILINE
        ),
        # Format 8 — "We're Hiring: Full Stack Developer (3–5 years...)"
        re.compile(
            r"(?:We(?:'re|\s+are)\s+(?:Hiring|Looking\s+For)[:\s]+)"
            r'([A-Z][A-Za-z0-9 /&\-\(\)–,]{2,80})',
            re.IGNORECASE
        ),
        # Format 19 — emoji prefix  👋 Hey, we're looking for a Platform Engineer!
        re.compile(
            r'looking\s+for\s+(?:a\s+|an\s+)?([A-Z][A-Za-z0-9 /&\-]{2,80}?)(?:[!,.]|$)',
            re.IGNORECASE
        ),
    ]

    # ------------------------------------------------------------------ #
    #  EXPERIENCE patterns                                                  #
    # ------------------------------------------------------------------ #
    _EXPERIENCE_PATTERNS = [
        # "5+ years", "5-7 years", "five years", "minimum 5 years of experience"
        re.compile(
            r'(?:minimum\s+of?\s*)?(\d+\+?\s*(?:to|\-|–)\s*\d+\s*years?'
            r'(?:\s+of)?(?:\s+relevant)?(?:\s+work)?\s*(?:experience|exp\.?))',
            re.IGNORECASE
        ),
        re.compile(
            r'(?:minimum\s+of?\s*)?(\d+\+\s*years?'
            r'(?:\s+of)?(?:\s+relevant)?(?:\s+work)?\s*(?:experience|exp\.?))',
            re.IGNORECASE
        ),
        re.compile(
            r'(\d+\s*years?(?:\s+of)?(?:\s+relevant)?(?:\s+work)?\s*(?:experience|exp\.?))',
            re.IGNORECASE
        ),
        # Format 16 — "Min. Experience: 5 Years | Preferred: 7 Years"
        re.compile(
            r'(?:Min(?:imum)?\.?\s*Experience|Experience\s*Required)\s*[:\-\.]+\s*(.+?)(?:\||$)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Format 14 — "3–5 Years | Healthcare IT Preferred"
        re.compile(
            r'Experience\s*[:\-\.]+\s*(\d+\s*(?:to|\-|–)\s*\d+\s*Years?[^\n]*)',
            re.IGNORECASE
        ),
        # "at least X years", "over X years"
        re.compile(
            r'(?:at\s+least|over|more\s+than)\s+(\d+\+?\s*years?\s*(?:of\s*)?(?:experience|exp\.?))',
            re.IGNORECASE
        ),
        # "(3–5 years experience preferred)" — parenthetical in title
        re.compile(
            r'\((\d+\+?\s*(?:to|\-|–)?\s*\d*\s*years?\s*(?:of\s*)?(?:experience|exp\.?)[^)]*)\)',
            re.IGNORECASE
        ),
        # "spent at least 4 years wrangling..."
        re.compile(
            r'spent\s+(?:at\s+least\s+)?(\d+\+?\s*years?)',
            re.IGNORECASE
        ),
    ]

    # ------------------------------------------------------------------ #
    #  SALARY patterns                                                      #
    # ------------------------------------------------------------------ #
    _SALARY_PATTERNS = [
        # Labeled: Salary / Compensation / Pay / Remuneration
        re.compile(
            r'(?:salary|compensation|pay(?:\s+range)?|remuneration|annual\s+compensation'
            r'|salary\s+band|salary\s+range|compensation\s+package)\s*[:\-\.]*\s*'
            r'((?:USD|GBP|EUR|AUD|CAD)?\s*'
            r'(?:\$|£|€|₹)?[\d,]+(?:K|k)?\s*(?:to|\-|–)\s*'
            r'(?:\$|£|€|₹)?[\d,]+(?:K|k)?'
            r'(?:\s*(?:per\s+(?:annum|year|month|hour)|p\.a\.|annually|\/yr|\/year|\/hr|\/hour))?'
            r'(?:[^\n]*(?:DOE|DOQ|commensurate|competitive|depending\s+on\s+experience))?)',
            re.IGNORECASE
        ),
        # Unlabeled range: $120,000 – $150,000 / $90K–$110K / £70,000 – £85,000
        re.compile(
            r'((?:USD|GBP|EUR|AUD|CAD)?\s*'
            r'(?:\$|£|€|₹)[\d,]+(?:K|k)?\s*(?:to|\-|–)\s*'
            r'(?:\$|£|€|₹)?[\d,]+(?:K|k)?'
            r'(?:\s*(?:per\s+(?:annum|year|month|hour)|p\.a\.|annually|\/yr|\/year|\/hr|\/hour))?)',
            re.IGNORECASE
        ),
        # Single figure: $105,000 annually / £85,000 per annum
        re.compile(
            r'((?:USD|GBP|EUR)?\s*(?:\$|£|€)[\d,]{4,}(?:K|k)?'
            r'\s*(?:per\s+(?:annum|year|month)|p\.a\.|annually|\/yr|\/year))',
            re.IGNORECASE
        ),
        # DOE / DOQ / Competitive / Commensurate with experience
        re.compile(
            r'(?:salary|compensation|pay)\s*[:\-]?\s*'
            r'((?:DOE|DOQ|Competitive|Commensurate\s+with\s+experience|'
            r'Depends?\s+on\s+(?:experience|qualifications)|Negotiable|TBD|Open))',
            re.IGNORECASE
        ),
        # Pipe-delimited format:  "| $90K–$115K |"
        re.compile(
            r'\|\s*((?:\$|£|€)[\d,]+(?:K|k)?\s*(?:\-|–)\s*(?:\$|£|€)?[\d,]+(?:K|k)?)\s*\|',
            re.IGNORECASE
        ),
        # Parenthetical in title: "($45,000–$55,000/yr)"
        re.compile(
            r'\(((?:\$|£|€)[\d,]+(?:K|k)?(?:\s*(?:\-|–)\s*(?:\$|£|€)?[\d,]+(?:K|k)?)?'
            r'(?:\/yr|\/year|\/hr|\/hour|p\.a\.)?)\)',
            re.IGNORECASE
        ),
    ]

    # ------------------------------------------------------------------ #
    #  LOCATION patterns                                                    #
    # ------------------------------------------------------------------ #
    _LOCATION_PATTERNS = [
        # Labeled: Location / Work Location / Job Location / Based in
        re.compile(
            r'(?:(?:work\s+)?location|job\s+location|office\s+location|based(?:\s+in)?|'
            r'primary\s+office|place\s+of\s+work)\s*[:\-\.]+\s*(.+?)(?:\n|$)',
            re.IGNORECASE
        ),
        # "📍 New York, NY"  or  "📍New York, NY"
        re.compile(
            r'📍\s*(.+?)(?:\s*\||\n|$)',
        ),
        # Dotted-aligned format:  "Work Location ............. Austin, TX 78701"
        re.compile(
            r'(?:work\s+)?location\s*\.{2,}\s*(.+?)(?:\n|$)',
            re.IGNORECASE
        ),
        # Pipe-delimited: "Senior QA Engineer | Remote | $95K"  → extract location segment
        re.compile(
            r'(?:^|\|)\s*((?:Remote(?:\s*[–\-]\s*\w+)?|Hybrid|On[\-\s]?[Ss]ite)'
            r'(?:\s*[\(\[/][^\)\]|]{1,60}[\)\]])?)\s*(?:\||$)',
            re.MULTILINE
        ),
        # "City, ST" or "City, Country" — two-word location with comma
        re.compile(
            r'\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-z]+))'
            r'(?:\s*[\(/](?:Hybrid|On[\-\s]?site|Remote)[^\)]*[\)])?',
        ),
        # "Remote" / "Remote – US Only" / "Fully Remote" alone on a segment
        re.compile(
            r'\b((?:Fully\s+)?Remote(?:\s*[\–\-/]\s*[A-Za-z/ ]{2,40})?'
            r'(?:\s*\([^)]{1,60}\))?)',
            re.IGNORECASE
        ),
        # "based out of Austin, TX" inline prose
        re.compile(
            r'based\s+(?:out\s+of\s+|in\s+)([A-Z][a-zA-Z\s,]+?)(?=\s+with|\s+and|\.|,\s+[a-z])',
        ),
    ]

    # ------------------------------------------------------------------ #
    #  BODY / DESCRIPTION section patterns                                  #
    # ------------------------------------------------------------------ #
    # These match the START of the body section. We grab everything after.
    _BODY_SECTION_HEADERS = re.compile(
        r'(?:^|\n)\s*(?:'
        r'Job\s*(?:Description|Summary|Overview|Details?)|'
        r'About\s+(?:the\s+)?(?:Role|Opportunity|Position|Company|us)|'
        r'Role\s+(?:Overview|Description|Summary)|'
        r'Position\s+(?:Summary|Description|Overview)|'
        r'Overview|'
        r'The\s+Role|'
        r'Responsibilities(?:\s+(?:Include|Overview))?|'
        r'What\s+You(?:\'ll|\ will)\s+Do|'
        r'Key\s+(?:Responsibilities|Duties)|'
        r'Scope\s+of\s+Work|'
        r'About\s+This\s+(?:Role|Position)|'
        r'Job\s+Purpose|'
        r'Purpose\s+of\s+(?:the\s+)?(?:Role|Position)'
        r')\s*[:\-]?\s*\n',
        re.IGNORECASE | re.MULTILINE
    )

    # Metadata-only lines to strip when isolating body
    _METADATA_LINE = re.compile(
        r'^\s*(?:'
        r'\[?(?:Job\s*Title|Position(?:\s*Title)?|Role|Title|Location|Work\s+Location'
        r'|Salary(?:\s+(?:Range|Band))?|Compensation|Pay(?:\s+Range)?'
        r'|Experience(?:\s+(?:Required|Level))?|Min(?:imum)?\.?\s*Experience'
        r'|Employment\s+Type|Job\s+(?:Code|Type|Grade)|Department|Team'
        r'|Duration|Reporting\s+To|Business\s+Unit|Grade\s+Level)\]?'
        r'\s*(?:[:\-\.]+|\.*)\s*.+|'
        r'(?:\|[^\|]+){2,}\|?'           # pipe-delimited header lines
        r')\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    # ------------------------------------------------------------------ #
    #  Constructor / public API                                             #
    # ------------------------------------------------------------------ #

    def __init__(self, job_id):
        self.job_id = job_id
        self.job = Job.objects.filter(id=self.job_id).first()
        self.description_text = ""

    def extract_pdf(self):
        if not self.job or not self.job.job_description_file:
            return ""

        file_path = self.job.job_description_file.path

        if file_path.endswith('.pdf'):
            self.description_text = handle_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.description_text = f.read()

        return self.description_text

    def regex_extraction(self):
        """
        Run all extraction patterns and return a dict with keys:
            title, experience, salary, location, description_body
        """
        if not self.description_text:
            self.extract_pdf()

        text = self.description_text

        return {
            'title':            self._extract_title(text),
            'experience':       self._extract_experience(text),
            'salary':           self._extract_salary(text),
            'location':         self._extract_location(text),
            'description_body': self._extract_body(text),
        }

    # ------------------------------------------------------------------ #
    #  Private extractors                                                   #
    # ------------------------------------------------------------------ #

    def _extract_title(self, text: str) -> str | None:
        for pattern in self._TITLE_PATTERNS:
            m = pattern.search(text)
            if m:
                candidate = m.group(1).strip()
                # Reject if it captured a sentence (too long or has sentence-ending punct mid-string)
                first_line = candidate.splitlines()[0].strip()
                # Reject if it's only noise/symbols
                if len(first_line) < 3 or re.match(r'^[\W\d]+$', first_line):
                    continue
                # Strip trailing punctuation clutter
                first_line = re.sub(r'[!.,;:]+$', '', first_line).strip()
                return first_line
        return None

    def _extract_experience(self, text: str) -> str | None:
        for pattern in self._EXPERIENCE_PATTERNS:
            m = pattern.search(text)
            if m:
                return m.group(1).strip()
        return None

    def _extract_salary(self, text: str) -> str | None:
        for pattern in self._SALARY_PATTERNS:
            m = pattern.search(text)
            if m:
                # Use group(1) if available, else full match
                value = (m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)).strip()
                # Sanity: must contain a digit or known keyword
                if re.search(r'\d|DOE|DOQ|Competitive|Commensurate|Negotiable', value, re.IGNORECASE):
                    return value
        return None

    def _extract_location(self, text: str) -> str | None:
        for pattern in self._LOCATION_PATTERNS:
            m = pattern.search(text)
            if m:
                loc = m.group(1).strip()
                # Strip trailing noise
                loc = re.sub(r'[\n\r|]+.*$', '', loc).strip()
                loc = re.sub(r'[.,;]+$', '', loc).strip()
                if len(loc) >= 3:
                    return loc
        return None

    def _extract_body(self, text: str) -> str:
        """
        Strategy:
        1. Find the first recognised body-section header and return everything after it.
        2. Fallback: strip obvious metadata lines from the top and return the rest.
        """
        header_match = self._BODY_SECTION_HEADERS.search(text)
        if header_match:
            body = text[header_match.end():].strip()
            return body

        # Fallback — remove metadata lines from the top until we hit real prose
        lines = text.splitlines()
        prose_start = 0
        for i, line in enumerate(lines):
            if self._METADATA_LINE.match(line) or not line.strip():
                continue
            # First line that is NOT a metadata label and NOT empty
            prose_start = i
            break

        return '\n'.join(lines[prose_start:]).strip()