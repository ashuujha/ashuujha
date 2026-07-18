import os
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def generate_typing_svg(texts, output_path):
    """Generates an SVG with a high-quality CSS typing animation."""
    # SVG size
    width = 850
    height = 70
    
    # Calculate timing
    num_phrases = len(texts)
    phrase_duration = 5.0  # seconds per phrase
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
    
    # Generate character animation keyframes
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        
        for j in range(L):
            t_char = t_start + (j / L) * 2.0  # Spend 2.0s typing
            t_visible = t_char + 0.05
            t_hide = t_end - 0.8  # Start fading out 0.8s before end
            
            # Convert to percentages
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
            
    # Cursor keyframes matching the text length
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        
        # Cursor positions along the text width
        # A single character width is roughly 12px for font-size 20px
        char_w = 12.0
        prompt_x = 240.0 # Approximate width of "ashuu1408@developer-os:~$ "
        
        for j in range(L + 1):
            t_cursor = t_start + (j / L) * 2.0 if j < L else t_start + 2.0
            t_hold_end = t_end - 0.8
            
            p_start = (t_cursor / total_duration) * 100
            p_end = (t_hold_end / total_duration) * 100
            
            # Keyframes to move cursor
            svg.append(f'    @keyframes cursor-p{i}-s{j} {{')
            svg.append(f'      0%, {p_start:.2f}% {{ transform: translateX({prompt_x + j * char_w:.1f}px); opacity: 1; }}')
            # If this is the last step in this phrase, hold position until fadeout
            if j == L:
                svg.append(f'      {p_start:.2f}%, {p_end:.2f}% {{ transform: translateX({prompt_x + L * char_w:.1f}px); opacity: 1; }}')
            else:
                next_t = t_start + ((j + 1) / L) * 2.0
                p_next = (next_t / total_duration) * 100
                svg.append(f'      {p_start:.2f}%, {p_next:.2f}% {{ transform: translateX({prompt_x + (j + 1) * char_w:.1f}px); opacity: 1; }}')
            svg.append(f'      {p_end:.2f}%, 100% {{ opacity: 0; }}')
            svg.append('    }')
            
    svg.append('  </style>')
    
    # Render prompt
    svg.append(f'  <text x="20" y="42" class="prompt">ashuu1408@developer-os:~$ </text>')
    
    # Render text characters
    for i, text in enumerate(texts):
        svg.append(f'  <!-- Phrase {i}: {text} -->')
        svg.append('  <text x="240" y="42" class="text">')
        for j, char in enumerate(text):
            # Escape spaces and HTML special chars
            char_disp = "&nbsp;" if char == " " else html_escape(char)
            svg.append(f'    <tspan class="p{i}-c{j}">{char_disp}</tspan>')
        svg.append('  </text>')
        
    # Render cursor (using a blinking box)
    # We will animate the cursor position using SMIL transform or a combined CSS classes
    # For simplicity, we can have one cursor element for each phrase that moves and is hidden during other phrases
    for i, text in enumerate(texts):
        L = len(text)
        t_start = i * phrase_duration
        t_end = (i + 1) * phrase_duration
        p_start = (t_start / total_duration) * 100
        p_end = (t_end / total_duration) * 100
        
        # CSS class to display cursor only during this phrase's active window
        svg.append('  <style>')
        svg.append(f'    @keyframes cursor-anim-{i} {{')
        # Sequence of cursor movement
        char_w = 12.0
        prompt_x = 240.0
        for j in range(L + 1):
            t_curr = t_start + (j / L) * 2.0 if j < L else t_start + 2.0
            p_curr = (t_curr / total_duration) * 100
            p_next_switch = (t_start + ((j + 1) / L) * 2.0 / total_duration) * 100 if j < L else p_end
            
            # Place cursor at position
            x_pos = prompt_x + j * char_w
            svg.append(f'      {p_curr:.2f}% {{ transform: translateX({x_pos:.1f}px); opacity: 1; }}')
            if j == L:
                t_hold = t_end - 0.8
                p_hold = (t_hold / total_duration) * 100
                svg.append(f'      {p_hold:.2f}% {{ transform: translateX({x_pos:.1f}px); opacity: 1; }}')
        # Outside active window, it should be invisible
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

def html_escape(char):
    if char == '&': return '&amp;'
    if char == '<': return '&lt;'
    if char == '>': return '&gt;'
    if char == '"': return '&quot;'
    return char

def fetch_rss_posts(feed_url, limit=3):
    """Fetches blog posts from RSS feeds (Medium, Dev.to, Hashnode)."""
    if not feed_url:
        return []
    print(f"Fetching blog posts from feed: {feed_url}...")
    posts = []
    try:
        req = urllib.request.Request(
            feed_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Handle RSS vs Atom
            items = root.findall('.//item')
            if not items:
                # Atom feed format
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                for item in items[:limit]:
                    title_elem = item.find('{http://www.w3.org/2005/Atom}title')
                    link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                    updated_elem = item.find('{http://www.w3.org/2005/Atom}updated')
                    
                    title = title_elem.text if title_elem is not None else "Untitled"
                    link = link_elem.attrib.get('href') if link_elem is not None else ""
                    
                    date_str = ""
                    if updated_elem is not None and updated_elem.text:
                        try:
                            # 2026-07-18T12:00:00Z
                            dt = datetime.strptime(updated_elem.text[:10], "%Y-%m-%d")
                            date_str = dt.strftime("%b %d, %Y")
                        except:
                            date_str = updated_elem.text[:10]
                            
                    if title and link:
                        posts.append((title, link, date_str))
            else:
                for item in items[:limit]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    
                    title = title_elem.text if title_elem is not None else "Untitled"
                    link = link_elem.text if link_elem is not None else ""
                    
                    date_str = ""
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            # Mon, 18 Jul 2026 12:00:00 GMT
                            dt = datetime.strptime(pub_date_elem.text[:16].strip(), "%a, %d %b %Y")
                            date_str = dt.strftime("%b %d, %Y")
                        except:
                            date_str = " ".join(pub_date_elem.text.split()[:4])
                            
                    if title and link:
                        posts.append((title, link, date_str))
    except Exception as e:
        print(f"Error fetching RSS: {e}")
    return posts

def generate_tech_stack_html(stack_dict):
    """Generates the Tech Stack using clean HTML <kbd> badges."""
    categories_map = {
      "languages": "💻 Languages",
      "backend": "⚙️ Backend",
      "frontend": "🎨 Frontend",
      "databases": "💾 Databases",
      "cloud": "☁️ Cloud Platforms",
      "devops": "♾️ DevOps & CI/CD",
      "ai_ml": "🧠 AI / ML",
      "tools": "🔧 Dev Tools",
      "learning": "📚 Learning Focus"
    }
    
    lines = []
    for key, category_name in categories_map.items():
        items = stack_dict.get(key, [])
        if items:
            kbd_badges = " ".join([f"<kbd>{item}</kbd>" for item in items])
            lines.append(f"- **{category_name}**:<br />{kbd_badges}")
            lines.append("")
            
    return "\n".join(lines)

def generate_projects_markdown(featured_dict):
    """Generates Featured Projects markdown lists."""
    lines = []
    
    # 1. Pinned / Most Starred Repos
    most_starred = featured_dict.get("most_starred", [])
    if most_starred:
        lines.append("### 🌟 Starred & Highlighted Repositories")
        lines.append("")
        for repo in most_starred:
            lines.append(f"#### 📂 [{repo['name']}]({repo['url']})")
            lines.append(f"> {repo['description']}")
            lines.append(f"- **Stack:** {repo['language']}")
            lines.append(f"- **Metrics:** ★ {repo['stars']}")
            lines.append("")
            
    # 2. Latest active project
    active = featured_dict.get("latest_active")
    if active:
        dt = datetime.strptime(active["pushed_at"], "%Y-%m-%dT%H:%M:%SZ") if "pushed_at" in active else datetime.now(timezone.utc).replace(tzinfo=None)
        date_str = dt.strftime("%B %Y")
        lines.append("### ⚡ Active Focus")
        lines.append("")
        lines.append(f"#### 📂 [{active['name']}]({active['url']})")
        lines.append(f"> {active['description']}")
        lines.append(f"- **Stack:** {active['language']}")
        lines.append(f"- **Last Updated:** {date_str} (Automated detection)")
        lines.append("")
        
    return "\n".join(lines)

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
        
    # 1. Generate typing header SVG
    typing_texts = config.get("typing_texts", ["Staff Software Engineer"])
    header_svg_path = os.path.join(base_dir, "assets", "header.svg")
    generate_typing_svg(typing_texts, header_svg_path)
    
    # 2. Read README.template.md
    template_path = os.path.join(base_dir, "doc", "README.template.md")
    with open(template_path, "r") as f:
        template = f.read()
        
    # Replace simple variables
    github_username = config.get("github_username", "ashuu1408")
    template = template.replace("{{GITHUB_USERNAME}}", github_username)
    
    # Last updated
    now = datetime.now(timezone.utc)
    last_updated = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    template = template.replace("{{LAST_UPDATED}}", last_updated)
    
    # About Section
    about_lines = [f"> {line}" for line in config.get("about", [])]
    template = template.replace("{{ABOUT}}", "\n".join(about_lines))
    
    # Tech Stack
    tech_stack_html = generate_tech_stack_html(config.get("tech_stack", {}))
    template = template.replace("{{TECH_STACK}}", tech_stack_html)
    
    # Featured Projects
    projects_markdown = generate_projects_markdown(stats.get("featured_projects", {}))
    template = template.replace("{{FEATURED_PROJECTS}}", projects_markdown)
    
    # Recent Activities
    activities = stats.get("recent_activities", [])
    activities_md = "\n".join([f"- {act}" for act in activities])
    template = template.replace("{{RECENT_ACTIVITY}}", activities_md)
    
    # Socials - styled like terminal menu
    socials = config.get("socials", {})
    social_links = []
    for platform, url in socials.items():
        if url and not url.startswith("https://placeholder"):
            # Format label as capitalized/uppercase
            label = platform.upper().replace("_", " ")
            # Bullet/Circle prompt
            social_links.append(f"[● {label}]({url})")
            
    socials_md = " &nbsp;&nbsp;&nbsp;&nbsp; ".join(social_links)
    template = template.replace("{{SOCIALS}}", socials_md)
    
    # WakaTime stats integration
    wakatime_user = config.get("wakatime_username", "")
    if wakatime_user:
        waka_md = (
            f'<img src="https://github-readme-stats.vercel.app/api/wakatime?username={wakatime_user}&amp;layout=compact&amp;theme=dark&amp;hide_border=true&amp;bg_color=0d1117&amp;title_color=58a6ff&amp;text_color=c9d1d9" alt="WakaTime Stats" width="80%" />'
        )
    else:
        waka_md = "*(WakaTime analytics not configured)*"
    template = template.replace("{{WAKATIME_STATS}}", waka_md)
    
    # Blog / Extras Section
    blog_config = config.get("blog", {})
    blog_posts = []
    
    # Try fetching from individual services
    if blog_config.get("rss_feed"):
        blog_posts.extend(fetch_rss_posts(blog_config["rss_feed"]))
    if blog_config.get("hashnode") and not blog_config.get("rss_feed"):
        # Hashnode RSS fallback
        blog_posts.extend(fetch_rss_posts(f"https://{blog_config['hashnode']}.hashnode.dev/rss.xml"))
    if blog_config.get("medium") and not blog_config.get("rss_feed"):
        blog_posts.extend(fetch_rss_posts(f"https://medium.com/feed/@{blog_config['medium']}"))
    if blog_config.get("devto") and not blog_config.get("rss_feed"):
        blog_posts.extend(fetch_rss_posts(f"https://dev.to/feed/{blog_config['devto']}"))
        
    extras_md = []
    if blog_posts:
        extras_md.append("## 📰 Latest Publications")
        extras_md.append("")
        for title, link, date in blog_posts:
            extras_md.append(f"- [{title}]({link}) ({date})")
        extras_md.append("")
        
    # YouTube channel Integration
    yt_id = config.get("youtube_channel_id", "")
    if yt_id:
        # Check if we can fetch latest videos from YouTube RSS feed
        yt_feed = f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_id}"
        yt_videos = fetch_rss_posts(yt_feed)
        if yt_videos:
            extras_md.append("## 🎥 Latest YouTube Uploads")
            extras_md.append("")
            for title, link, date in yt_videos:
                # YouTube feeds put date as updated
                extras_md.append(f"- [▶️ {title}]({link})")
            extras_md.append("")
            
    template = template.replace("{{EXTRAS_SECTION}}", "\n".join(extras_md))
    
    # 3. Write final README.md
    readme_output_path = os.path.join(base_dir, "README.md")
    with open(readme_output_path, "w") as f:
        f.write(template)
    print(f"Dashboard README.md generated successfully at {readme_output_path}")

if __name__ == "__main__":
    main()
