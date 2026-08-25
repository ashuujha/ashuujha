import os
import json
import re
import html
from datetime import datetime, timezone

def generate_typing_svg(texts, output_path):
    """Generates an SVG with a high-quality CSS typing animation."""
    width = 850
    height = 70
    
    num_phrases = len(texts)
    phrase_duration = 5.0
    total_duration = num_phrases * phrase_duration
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">')
    svg.append('  <style>')
    svg.append('    :root {')
    svg.append('      --color-prompt: #58a6ff;')
    svg.append('      --color-text: #c9d1d9;')
    svg.append('      --color-cursor: #58a6ff;')
    svg.append('      --color-bg: #0d1117;')
    svg.append('    }')
    svg.append('    @media (prefers-color-scheme: light) {')
    svg.append('      :root {')
    svg.append('        --color-prompt: #0969da;')
    svg.append('        --color-text: #24292f;')
    svg.append('        --color-cursor: #0969da;')
    svg.append('        --color-bg: #ffffff;')
    svg.append('      }')
    svg.append('    }')
    svg.append('    .prompt {')
    svg.append('      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;')
    svg.append('      font-size: 20px;')
    svg.append('      fill: var(--color-prompt);')
    svg.append('      font-weight: bold;')
    svg.append('    }')
    svg.append('    .text {')
    svg.append('      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;')
    svg.append('      font-size: 20px;')
    svg.append('      fill: var(--color-text);')
    svg.append('    }')
    svg.append('    .cursor {')
    svg.append('      fill: var(--color-cursor);')
    svg.append(f'      animation: blink 0.8s infinite;')
    svg.append('    }')
    svg.append('    @keyframes blink {')
    svg.append('      0%, 49% { opacity: 1; }')
    svg.append('      50%, 100% { opacity: 0; }')
    svg.append('    }')
    
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        
        for j in range(L):
            t_char = t_start + (j / L) * 2.0
            t_visible = t_char + 0.05
            t_hide = t_end - 0.8
            
            p_start = (t_char / total_duration) * 100
            p_visible = (t_visible / total_duration) * 100
            p_hide = (t_hide / total_duration) * 100
            p_end = (t_end / total_duration) * 100
            
            svg.append(f'    @keyframes type-p{i}-c{j} {{')
            svg.append(f'      0%, {p_start:.2f}% {{ opacity: 0; }}')
            svg.append(f'      {p_visible:.2f}%, {p_hide:.2f}% {{ opacity: 1; }}')
            svg.append(f'      {p_end:.2f}%, 100% {{ opacity: 0; }}')
            svg.append('    }')
            svg.append(f'    .p{i}-c{j} {{ animation: type-p{i}-c{j} {total_duration:.2f}s infinite; }}')
            
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        
        char_w = 12.0
        prompt_x = 240.0
        
        for j in range(L + 1):
            t_cursor = t_start + (j / L) * 2.0 if j < L else t_start + 2.0
            t_hold_end = t_end - 0.8
            
            p_start = (t_cursor / total_duration) * 100
            p_end = (t_hold_end / total_duration) * 100
            
            svg.append(f'    @keyframes cursor-p{i}-s{j} {{')
            svg.append(f'      0%, {p_start:.2f}% {{ transform: translateX({prompt_x + j * char_w:.1f}px); opacity: 1; }}')
            if j == L:
                svg.append(f'      {p_start:.2f}%, {p_end:.2f}% {{ transform: translateX({prompt_x + L * char_w:.1f}px); opacity: 1; }}')
            else:
                next_t = t_start + ((j + 1) / L) * 2.0
                p_next = (next_t / total_duration) * 100
                svg.append(f'      {p_start:.2f}%, {p_next:.2f}% {{ transform: translateX({prompt_x + (j + 1) * char_w:.1f}px); opacity: 1; }}')
            svg.append(f'      {p_end:.2f}%, 100% {{ opacity: 0; }}')
            svg.append('    }')
            
    svg.append('  </style>')
    
    svg.append(f'  <text x="20" y="42" class="prompt">ashuujha@developer-os:~$ </text>')
    
    for i, text in enumerate(texts):
        svg.append(f'  <!-- Phrase {i}: {text} -->')
        svg.append('  <text x="240" y="42" class="text">')
        for j, char in enumerate(text):
            char_disp = "&nbsp;" if char == " " else html_escape(char)
            svg.append(f'    <tspan class="p{i}-c{j}">{char_disp}</tspan>')
        svg.append('  </text>')
        
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        p_start = (t_start / total_duration) * 100
        p_end = (t_end / total_duration) * 100
        
        svg.append('  <style>')
        svg.append(f'    @keyframes cursor-anim-{i} {{')
        char_w = 12.0
        prompt_x = 240.0
        for j in range(L + 1):
            t_curr = t_start + (j / L) * 2.0 if j < L else t_start + 2.0
            p_curr = (t_curr / total_duration) * 100
            p_next_switch = (t_start + ((j + 1) / L) * 2.0 / total_duration) * 100 if j < L else p_end
            
            x_pos = prompt_x + j * char_w
            svg.append(f'      {p_curr:.2f}% {{ transform: translateX({x_pos:.1f}px); opacity: 1; }}')
            if j == L:
                t_hold = t_end - 0.8
                p_hold = (t_hold / total_duration) * 100
                svg.append(f'      {p_hold:.2f}% {{ transform: translateX({x_pos:.1f}px); opacity: 1; }}')
        svg.append(f'      0%, {p_start:.2f}% {{ opacity: 0; }}')
        svg.append(f'      {p_end:.2f}%, 100% {{ opacity: 0; }}')
        svg.append('    }')
        svg.append(f'    .cursor-{i} {{ animation: cursor-anim-{i} {total_duration:.2f}s infinite; }}')
        svg.append('  </style>')
        svg.append(f'  <rect x="0" y="24" width="10" height="20" class="cursor cursor-{i}" />')
        
    svg.append('</svg>')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Typing animation header saved to {output_path}")

def generate_github_stats_svg(stats, output_path):
    """Generates a dark-themed SVG card for GitHub statistics."""
    width = 400
    height = 200
    bg_color = "#0d1117"
    border_color = "#30363d"
    title_color = "#58a6ff"
    text_color = "#c9d1d9"
    stat_val_color = "#58a6ff"
    
    items = [
        ("Total Commits", str(stats.get("total_commits", "0"))),
        ("Public Repositories", str(stats.get("public_repos", 0))),
        ("Followers", str(stats.get("followers", 0))),
        ("Stars Earned", str(stats.get("stars_earned", 0))),
        ("Pull Requests", str(stats.get("total_prs", 0))),
        ("Issues / Reviews", f"{stats.get('total_issues', 0)} / {stats.get('total_reviews', 0)}")
    ]
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .card-title {{ font-family: SFMono-Regular, Consolas, monospace; font-size: 15px; font-weight: bold; fill: {title_color}; }}')
    svg.append(f'    .stat-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; fill: {text_color}; }}')
    svg.append(f'    .stat-val {{ font-family: SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: bold; fill: {stat_val_color}; }}')
    svg.append('  </style>')
    svg.append(f'  <rect width="{width}" height="{height}" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" />')
    svg.append(f'  <text x="20" y="32" class="card-title">⚡ GitHub Stats</text>')
    
    y = 62
    for label, val in items:
        svg.append(f'  <text x="25" y="{y}" class="stat-label">{label}</text>')
        svg.append(f'  <text x="{width - 25}" y="{y}" text-anchor="end" class="stat-val">{val}</text>')
        y += 22
        
    svg.append('</svg>')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg))
    print(f"GitHub Stats SVG saved to {output_path}")

def generate_top_languages_svg(stats, output_path):
    """Generates a dark-themed SVG card for Top Languages."""
    width = 400
    height = 200
    bg_color = "#0d1117"
    border_color = "#30363d"
    title_color = "#58a6ff"
    text_color = "#c9d1d9"
    
    lang_colors = {
        "Go": "#00ADD8",
        "Python": "#3572A5",
        "Rust": "#dea584",
        "TypeScript": "#3178c6",
        "JavaScript": "#f1e05a",
        "C++": "#f34b7d",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Shell": "#89e051"
    }
    
    top_langs = stats.get("top_languages", ["Go", "Python", "Rust", "TypeScript", "JavaScript"])[:5]
    if not top_langs:
        top_langs = ["Go", "Python", "Rust", "TypeScript"]
        
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .card-title {{ font-family: SFMono-Regular, Consolas, monospace; font-size: 15px; font-weight: bold; fill: {title_color}; }}')
    svg.append(f'    .lang-name {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; fill: {text_color}; }}')
    svg.append('  </style>')
    svg.append(f'  <rect width="{width}" height="{height}" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" />')
    svg.append(f'  <text x="20" y="32" class="card-title">🚀 Top Languages</text>')
    
    y = 60
    for lang in top_langs:
        color = lang_colors.get(lang, "#8b949e")
        svg.append(f'  <circle cx="30" cy="{y - 4}" r="5" fill="{color}" />')
        svg.append(f'  <text x="45" y="{y}" class="lang-name">{lang}</text>')
        svg.append(f'  <rect x="160" y="{y - 11}" width="215" height="8" rx="4" fill="#21262d" />')
        svg.append(f'  <rect x="160" y="{y - 11}" width="160" height="8" rx="4" fill="{color}" />')
        y += 26
        
    svg.append('</svg>')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Top Languages SVG saved to {output_path}")

def html_escape(char):
    if char == '&': return '&amp;'
    if char == '<': return '&lt;'
    if char == '>': return '&gt;'
    if char == '"': return '&quot;'
    return char

def replace_section(content, marker_name, new_inner_content):
    """Replaces content strictly between <!--START_SECTION:marker_name--> and <!--END_SECTION:marker_name-->."""
    start_marker = f"<!--START_SECTION:{marker_name}-->"
    end_marker = f"<!--END_SECTION:{marker_name}-->"
    
    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    replacement = f"{start_marker}\n{new_inner_content}\n{end_marker}"
    
    if pattern.search(content):
        return pattern.sub(replacement, content)
    else:
        # If marker does not exist in target file, append section
        print(f"Warning: Section marker {marker_name} not found in README.md. Appending section.")
        return content + f"\n\n{replacement}"

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Load config and stats
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
        
    stats_path = os.path.join(base_dir, "assets", "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r") as f:
            stats = json.load(f)
    else:
        print("Warning: stats.json not found. Run fetch_stats.py first.")
        stats = {}
        
    # 1. Generate typing header SVG & metric card SVGs
    typing_texts = config.get("typing_texts", ["Creative Developer"])
    header_svg_path = os.path.join(base_dir, "assets", "header.svg")
    generate_typing_svg(typing_texts, header_svg_path)
    
    stats_svg_path = os.path.join(base_dir, "assets", "github_stats.svg")
    generate_github_stats_svg(stats, stats_svg_path)
    
    langs_svg_path = os.path.join(base_dir, "assets", "top_languages.svg")
    generate_top_languages_svg(stats, langs_svg_path)
    
    # 2. Target existing README.md (or fallback to doc/README.template.md)
    readme_path = os.path.join(base_dir, "README.md")
    template_path = os.path.join(base_dir, "doc", "README.template.md")
    
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
    elif os.path.exists(template_path):
        with open(template_path, "r") as f:
            content = f.read()
    else:
        print("Error: Neither README.md nor doc/README.template.md found.")
        return

    # Prepare inner contents for each section
    
    # About Section
    about_lines = [f"> {line}" for line in config.get("about", [])]
    about_inner = "<!-- About Section -->\n## 👤 About\n\n" + "\n".join(about_lines)
    
    # Live GitHub Metrics Section
    metrics_inner = (
        "<!-- GitHub Analytics / Dashboard -->\n"
        "## Live GitHub Metrics\n\n"
        '<div align="center">\n'
        '  <img src="./assets/github_stats.svg" width="48%" alt="GitHub Stats" />\n'
        '  <img src="./assets/top_languages.svg" width="48%" alt="Top Languages" />\n'
        '</div>'
    )
    
    # Recent Activities (Kernel Logs)
    activities = stats.get("recent_activities", [])
    activities_md = "\n".join([f"- {act}" for act in activities])
    activity_inner = "<!-- Recent Activity -->\n## Latest Kernel Logs (Recent Activity)\n\n" + activities_md
    
    # Footer Section
    now = datetime.now(timezone.utc)
    last_updated = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    footer_inner = f'<br />\n\n<div align="center">\n  <sub>Last updated: <i>{last_updated}</i> | System status: <b>Operational</b></sub>\n</div>'
    
    # Apply targeted section replacements
    content = replace_section(content, "about", about_inner)
    content = replace_section(content, "metrics", metrics_inner)
    content = replace_section(content, "activity", activity_inner)
    content = replace_section(content, "footer", footer_inner)
    
    # Save back to README.md
    with open(readme_path, "w") as f:
        f.write(content)
        
    print(f"Targeted section update completed successfully for {readme_path}")

if __name__ == "__main__":
    main()
