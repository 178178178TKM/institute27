#!/usr/bin/env python3
"""
ç¬¬å¼æ¾ä¸ç ç©¶æ â çµ±åè¨é²ãã«ãã·ã¹ãã 
JSON ãã¼ã¿ãã index.html ãçæãã

ä½¿ãæ¹:
  python build.py                    # template.html â index.html
  python build.py --validate         # JSONãã¼ã¿ã®æ´åæ§ãã§ãã¯ã®ã¿
  python build.py --dry-run          # çæHTMLãstdoutã«åºå
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# âââ ãã¹è¨­å® âââ
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_FILE = BASE_DIR / "template.html"
OUTPUT_FILE = BASE_DIR / "index.html"


def load_json(filename):
    """JSONãã¡ã¤ã«ãèª­ã¿è¾¼ã"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"â  ãã¡ã¤ã«ãè¦ã¤ããã¾ãã: {filepath}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  HTMLçæ: Featured Articlesï¼ãããè¨äºï¼
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_featured_card(article, is_first=False):
    """Featuredè¨äºã®HTMLã«ã¼ããçæ"""
    
    type_code = article["type"]
    case_num = article.get("case_number", "")
    case_display = f"Case#{case_num}" if case_num else article["id"]
    level = article.get("level", 0)
    status = article.get("status", "ACTIVE")
    
    # ã¹ãã¼ã¿ã¹ã©ãã«
    status_class = status.lower()
    status_label = {
        "ACTIVE": "èª¿æ»ç¶ç¶ä¸­" if type_code == "IC" else "è¦³æ¸¬ç¶ç¶ä¸­",
        "ARCHIVED": "å®äº",
        "PENDING": "ä¿çä¸­",
        "REDACTED": "REDACTED"
    }.get(status, status)
    
    # ã¡ã¿ãã¼ã¿è¡
    meta_items = []
    meta_items.append(f'<div class="meta-item"><span class="meta-label">åé¡:</span> {article["type_label"]}</div>')
    meta_items.append(f'<div class="meta-item"><span class="meta-label">æå½èª²:</span> {article["department"]}</div>')
    meta_items.append(f'<div class="meta-item"><span class="meta-label">æå½è:</span> {article["assignee"]}</div>')
    meta_items.append(f'<div class="meta-item"><span class="meta-label">é²è¦§Level:</span> Level {level}</div>')
    for key, val in article.get("metadata", {}).items():
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{key}:</span> {val}</div>')
    meta_items.append(f'<div class="meta-item"><span class="meta-label">ç¶æ:</span> {status}</div>')
    meta_html = "\n                    ".join(meta_items)
    
    # é¢é£è¨é²
    related_html = ""
    if article.get("related"):
        related_links = []
        for r in article["related"]:
            related_links.append(f'{r["id"]} {r["title"]}')
        related_html = f"""
                <div class="case-related">
                    <h4>é¢é£è¨é²</h4>
                    <p>{"<br>".join(related_links)}</p>
                </div>"""
    
    # ã¬ãã¼ãé¨å
    report_html = ""
    if article.get("report"):
        rpt = article["report"]
        sections_html = ""
        for sec in rpt.get("sections", []):
            warning = ""
            if sec.get("warning"):
                warning = f'\n                        <p class="report-warning">â  {sec["warning"]}</p>'
            note = ""
            if sec.get("note"):
                note = f'\n                        <p class="report-note">â  {sec["note"]}</p>'
            sections_html += f"""
                    <div class="report-section">
                        <h3>â {sec["title"]}</h3>
                        <p>{sec["content"]}</p>{warning}{note}
                    </div>"""
        
        report_html = f"""
            <div class="investigation-report">
                <div class="report-label">// èª¿æ»ã¬ãã¼ãæç² â {article["id"]}</div>
                <div class="report-header">
                    <p>{rpt["header"]}</p>
                    <p class="report-subheader">{rpt["subheader"]}</p>
                </div>{sections_html}
            </div>"""
    
    # ã«ã¼ãå¨ä¼
    latest_marker = ""
    if is_first:
        latest_marker = f"""
            <div class="case-label">LATEST ï¼ {article["id"]} ï¼ {case_display} ï¼ {article["department"]}</div>"""
    else:
        latest_marker = f"""
            <div class="case-label">{article["id"]} ï¼ {case_display} ï¼ {article["department"]}</div>"""
    
    html = f"""
        <article class="case-card featured-case" data-level="{level}" data-type="{type_code}" data-id="{article["id"]}">
            {latest_marker}
            <h2 class="case-title">{article["title"]}</h2>
            <div class="case-tags">
                <span class="tag tag-type">{type_code}</span>
                <span class="tag tag-status tag-{status_class}">{status_label}</span>
                <span class="tag tag-assignee">æå½: {article["assignee"]}</span>
                <span class="tag tag-date">åå ±: {article.get("first_report", "")}</span>
            </div>
            <div class="case-summary">
                <p>{article["summary"]}</p>
                <p>{article.get("summary_extra", "")}</p>
            </div>
            <div class="case-metadata">
                <h4>æ¡ä»¶ãã¼ã¿</h4>
                <div class="meta-grid">
                    {meta_html}
                </div>
            </div>{related_html}{report_html}
        </article>"""
    
    return html


def build_featured_section(articles):
    """Featuredè¨äºã»ã¯ã·ã§ã³å¨ä½ãçæ"""
    cards = []
    for i, article in enumerate(articles):
        cards.append(build_featured_card(article, is_first=(i == 0)))
    return "\n".join(cards)


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  HTMLçæ: Archive Indexï¼è¨é²ä¸è¦§ï¼
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_archive_item(article):
    """ã¢ã¼ã«ã¤ãä¸è¦§ã®1é ç®ãçæ"""
    
    type_code = article["type"]
    level = article.get("level", 0)
    status = article.get("status", "ACTIVE")
    
    # REDACTEDè¨äº
    if article.get("redacted", False):
        return f"""
        <div class="archive-item archive-redacted" data-level="{level}" data-type="{type_code}">
            <div class="archive-item-header">
                <span class="archive-type">{type_code}</span>
                <span class="archive-case">Case#{article.get("case_number", "???")}</span>
            </div>
            <h3 class="archive-title">{article["title"]}</h3>
            <p class="archive-denied">â ACCESS DENIED â Level {level} required</p>
            <div class="archive-tags">
                <span class="tag tag-redacted">REDACTED</span>
                <span class="tag tag-level">Level {level}</span>
            </div>
        </div>"""
    
    # éå¸¸è¨äº
    status_class = status.lower()
    assignee_html = ""
    if article.get("assignee"):
        dept = article.get("department", "")
        assignee_html = f"æå½: {article['assignee']}ï¼{dept}ï¼" if dept else f"æå½: {article['assignee']}"
    elif article.get("department"):
        assignee_html = f"ä½æ: {article['department']}"
    
    case_display = ""
    if article.get("case_number"):
        case_display = f'<span class="archive-case">Case#{article["case_number"]}</span>'
    
    return f"""
        <div class="archive-item" data-level="{level}" data-type="{type_code}" data-id="{article["id"]}">
            <div class="archive-item-header">
                <span class="archive-type">{type_code}</span>
                {case_display}
            </div>
            <h3 class="archive-title">{article["title"]}</h3>
            <p class="archive-summary">{article.get("summary", "")}</p>
            <div class="archive-tags">
                <span class="tag tag-status tag-{status_class}">{status}</span>
                <span class="tag tag-assignee">{assignee_html}</span>
            </div>
        </div>"""


def build_archive_section(articles):
    """ã¢ã¼ã«ã¤ãä¸è¦§ã»ã¯ã·ã§ã³å¨ä½ãçæ"""
    items = []
    for article in articles:
        items.append(build_archive_item(article))
    return "\n".join(items)


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  HTMLçæ: Glossaryï¼ç¨èªéï¼
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_glossary_section(glossary_data):
    """ç¨èªéã»ã¯ã·ã§ã³ãçæ"""
    if not glossary_data or not glossary_data.get("terms"):
        return "<!-- ç¨èªãªã -->"
    
    items = []
    for term in glossary_data["terms"]:
        related_html = ""
        if term.get("related"):
            related_tags = " ".join([f'<span class="glossary-related-tag">{r}</span>' for r in term["related"]])
            related_html = f'\n                <div class="glossary-related">é¢é£: {related_tags}</div>'
        
        items.append(f"""
            <div class="glossary-item">
                <h3 class="glossary-term">{term["term"]}</h3>
                <p class="glossary-reading">{term["reading"]} / {term["english"]}</p>
                <p class="glossary-definition">{term["definition"]}</p>{related_html}
            </div>""")
    
    return "\n".join(items)


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  HTMLçæ: Referencesï¼åèæç®ï¼
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_references_section(references_data):
    """åèæç®ã»ã¯ã·ã§ã³ãçæ"""
    if not references_data or not references_data.get("books"):
        return "<!-- åèæç®ãªã -->"
    
    items = []
    for book in references_data["books"]:
        url = book.get("amazon_url", "#")
        items.append(f"""
            <div class="reference-item">
                <h3 class="reference-title">{book["title"]}</h3>
                <p class="reference-author">{book["author"]}</p>
                <p class="reference-description">{book["description"]}</p>
                <a href="{url}" class="reference-link" target="_blank" rel="noopener">Amazon ã§ç¢ºèª â</a>
                <p class="reference-affiliate">â» Amazonã¢ã½ã·ã¨ã¤ãåå </p>
            </div>""")
    
    return "\n".join(items)


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  HTMLçæ: Organizationï¼çµç¹æ¦è¦ï¼
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_organization_section(org_data):
    """çµç¹æ¦è¦ã»ã¯ã·ã§ã³ãçæ"""
    if not org_data:
        return "<!-- çµç¹ãã¼ã¿ãªã -->"
    
    # ãªã¼ãã¼ã·ãã
    leadership = org_data.get("leadership", [])
    leadership_parts = []
    for leader in leadership:
        depts = "ã»".join(leader["departments"])
        leadership_parts.append(f"â {leader['jurisdiction']}ï¼{leader['name']}ï¼: {depts}")
    leadership_html = " ï¼ ".join(leadership_parts)
    
    # é¨ç½²
    dept_cards = []
    for dept in org_data.get("departments", []):
        dept_cards.append(f"""
            <div class="org-dept-card">
                <h3>{dept["name"]} ï¼ {dept["english"]}</h3>
                <p class="org-chief">{dept["chief"]}ãèª²é·ã</p>
                <p class="org-staff">å¨ç±{dept["staff_count"]}å</p>
                <p class="org-desc">{dept["description"]}</p>
            </div>""")
    
    return f"""
        <p class="org-leadership">{leadership_html}</p>
        <div class="org-grid">
            {"".join(dept_cards)}
        </div>"""


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  ãã³ãã¬ã¼ãå¦ç
# âââââââââââââââââââââââââââââââââââââââââââââââ

def build_html(template_content, replacements):
    """ãã³ãã¬ã¼ãã«ã³ã³ãã³ããæ¿å¥"""
    result = template_content
    for key, value in replacements.items():
        placeholder = f"{{{{{{ {key} }}}}}}"  # {{{ KEY }}}
        # å®éã«ã¯ã·ã³ãã«ãªãã¬ã¼ã¹ãã«ããä½¿ç¨
        marker = f"<!-- BUILD:{key} -->"
        result = result.replace(marker, value)
    return result


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  ããªãã¼ã·ã§ã³
# âââââââââââââââââââââââââââââââââââââââââââââââ

def validate_article(article, context=""):
    """è¨äºãã¼ã¿ã®å¦¥å½æ§ãæ¤è¨¼"""
    errors = []
    required = ["id", "type", "title"]
    for field in required:
        if not article.get(field):
            errors.append(f"{context} å¿é ãã£ã¼ã«ã '{field}' ãæªè¨­å®")
    
    valid_types = ["IC", "PH", "EN", "AN", "FL"]
    if article.get("type") and article["type"] not in valid_types:
        errors.append(f"{context} ä¸æ­£ãª type: {article['type']} (æå¹å¤: {valid_types})")
    
    valid_statuses = ["ACTIVE", "ARCHIVED", "PENDING", "REDACTED"]
    if article.get("status") and article["status"] not in valid_statuses:
        errors.append(f"{context} ä¸æ­£ãª status: {article['status']}")
    
    if article.get("level") is not None:
        if not isinstance(article["level"], int) or article["level"] < 0 or article["level"] > 5:
            errors.append(f"{context} level ã¯ 0-5 ã®æ´æ°: {article['level']}")
    
    return errors


def validate_all():
    """å¨ãã¼ã¿ã®æ´åæ§ãã§ãã¯"""
    print("âââ ãã¼ã¿æ¤è¨¼éå§ âââ")
    all_errors = []
    all_ids = set()
    
    # Articles
    articles = load_json("articles.json")
    if articles:
        for i, art in enumerate(articles.get("featured", [])):
            ctx = f"featured[{i}] ({art.get('id', '?')})"
            all_errors.extend(validate_article(art, ctx))
            if art.get("id"):
                if art["id"] in all_ids:
                    all_errors.append(f"{ctx} IDéè¤: {art['id']}")
                all_ids.add(art["id"])
        
        for i, art in enumerate(articles.get("archive", [])):
            ctx = f"archive[{i}] ({art.get('id', '?')})"
            all_errors.extend(validate_article(art, ctx))
            if art.get("id"):
                if art["id"] in all_ids:
                    all_errors.append(f"{ctx} IDéè¤: {art['id']}")
                all_ids.add(art["id"])
    
    # Glossary
    glossary = load_json("glossary.json")
    if glossary:
        for i, term in enumerate(glossary.get("terms", [])):
            if not term.get("term"):
                all_errors.append(f"glossary[{i}] 'term' ãæªè¨­å®")
    
    # Summary
    total_articles = 0
    if articles:
        total_articles = len(articles.get("featured", [])) + len(articles.get("archive", []))
    
    print(f"  è¨äºæ°: {total_articles} ({len(articles.get('featured', []))} featured + {len(articles.get('archive', []))} archive)")
    print(f"  ç¨èªæ°: {len(glossary.get('terms', [])) if glossary else 0}")
    print(f"  åèæç®: {len(load_json('references.json').get('books', [])) if load_json('references.json') else 0}")
    
    if all_errors:
        print(f"\nâ  ã¨ã©ã¼ {len(all_errors)}ä»¶:")
        for err in all_errors:
            print(f"  â {err}")
        return False
    else:
        print("\nâ ããªãã¼ã·ã§ã³éé")
        return True


# âââââââââââââââââââââââââââââââââââââââââââââââ
#  ã¡ã¤ã³å¦ç
# âââââââââââââââââââââââââââââââââââââââââââââââ

def main():
    # å¼æ°å¦ç
    if "--validate" in sys.argv:
        validate_all()
        return
    
    dry_run = "--dry-run" in sys.argv
    
    print("âââ ç¬¬å¼æ¾ä¸ç ç©¶æ ãã«ãã·ã¹ãã  âââ")
    print(f"  æ¥æ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ããªãã¼ã·ã§ã³
    if not validate_all():
        print("\nâ  ã¨ã©ã¼ãããã¾ãã--force ã§å¼·å¶ãã«ãå¯è½")
        if "--force" not in sys.argv:
            return
    
    print()
    
    # ãã¼ã¿èª­ã¿è¾¼ã¿
    articles = load_json("articles.json")
    glossary = load_json("glossary.json")
    references = load_json("references.json")
    organization = load_json("organization.json")
    
    # HTMLçæ
    print("HTMLãçæä¸­...")
    
    featured_html = build_featured_section(articles.get("featured", []))
    archive_html = build_archive_section(articles.get("archive", []))
    glossary_html = build_glossary_section(glossary)
    references_html = build_references_section(references)
    organization_html = build_organization_section(organization)
    
    # ãã«ãæ¥æ
    build_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # ãã³ãã¬ã¼ãèª­ã¿è¾¼ã¿ & ç½®æ
    if not TEMPLATE_FILE.exists():
        print(f"â  ãã³ãã¬ã¼ããè¦ã¤ããã¾ãã: {TEMPLATE_FILE}")
        print("  â ãã³ãã¬ã¼ããä½æãã¦ãã ããï¼READMEåç§ï¼")
        
        # ãã©ã¼ã«ããã¯: åã»ã¯ã·ã§ã³ã®HTMLãåå¥ãã¡ã¤ã«ã«åºå
        output_dir = BASE_DIR / "build_output"
        output_dir.mkdir(exist_ok=True)
        
        sections = {
            "featured.html": featured_html,
            "archive.html": archive_html,
            "glossary.html": glossary_html,
            "references.html": references_html,
            "organization.html": organization_html,
        }
        
        for filename, content in sections.items():
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  â {output_dir / filename}")
        
        print(f"\nåã»ã¯ã·ã§ã³ã®HTMLã {output_dir}/ ã«åºåãã¾ããã")
        print("template.html ãç¨æããã°ãä¸æ¬ãã«ããå¯è½ã«ãªãã¾ãã")
        return
    
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    
    replacements = {
        "FEATURED_ARTICLES": featured_html,
        "ARCHIVE_INDEX": archive_html,
        "GLOSSARY_TERMS": glossary_html,
        "REFERENCES_LIST": references_html,
        "ORGANIZATION_CONTENT": organization_html,
        "BUILD_TIMESTAMP": build_timestamp,
        "ARTICLE_COUNT": str(len(articles.get("featured", [])) + len(articles.get("archive", []))),
    }
    
    output = build_html(template, replacements)
    
    if dry_run:
        print(output)
    else:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"â {OUTPUT_FILE} ãçæãã¾ãã")
        print(f"  ãµã¤ãº: {os.path.getsize(OUTPUT_FILE):,} bytes")
    
    print("\nâââ ãã«ãå®äº âââ")


if __name__ == "__main__":
    main()
