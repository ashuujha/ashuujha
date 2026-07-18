import os
import json
import html
from datetime import datetime, timezone

def load_stats_and_config():
    """Loads the config and stats JSON files."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
        
    stats_path = os.path.join(base_dir, "assets", "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "name": config.get("name", "Ashutosh Jha"),
            "uptime": "Unknown",
            "location": config.get("location", "India"),
            "public_repos": 0,
            "followers": 0,
            "following": 0,
            "stars_earned": 0,
            "total_commits": "0",
            "total_prs": "0",
            "total_issues": "0",
            "total_reviews": "0",
            "most_used_language": "Unknown"
        }
    return config, stats

def load_ascii_art():
    """Loads ASCII art from assets/ascii_art.txt."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ascii_path = os.path.join(base_dir, "assets", "ascii_art.txt")
    if os.path.exists(ascii_path):
        with open(ascii_path, "r") as f:
            return f.read().splitlines()
    else:
        # Fallback simple logo if avatar conversion is missing
        return [
            "    .--------.    ",
            "   /          \\   ",
            "  |   O    O   |  ",
            "  |     ||     |  ",
            "  |   \\____/   |  ",
            "   \\          /   ",
            "    '--------'    "
        ]

def format_neofetch_lines(config, stats):
    """Formats the Neofetch text lines."""
    username = config.get("github_username", "ashuu1408")
    
    # Formatted last updated time (local time of runner or UTC)
    now = datetime.now(timezone.utc)
    last_updated = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Extract config lists
    languages = ", ".join(config.get("tech_stack", {}).get("languages", [])[:6])
    frameworks = ", ".join(config.get("tech_stack", {}).get("backend", [])[:3] + config.get("tech_stack", {}).get("frontend", [])[:3])
    databases = ", ".join(config.get("tech_stack", {}).get("databases", [])[:3])
    devops = ", ".join(config.get("tech_stack", {}).get("devops", [])[:3])
    cloud = ", ".join(config.get("tech_stack", {}).get("cloud", [])[:2])
    focus = config.get("typing_texts", ["Software Engineering"])[-1]
    
    lines = [
        f"{username}@developer-os",
        "-" * (len(username) + 13),
        ("OS", "Linux (Ubuntu / Alpine / Debian)"),
        ("Uptime (GitHub age)", stats.get("uptime", "Unknown")),
        ("Shell", "bash / zsh / fish"),
        ("Editor", "Neovim / VS Code"),
        "",
        ("Languages", languages),
        ("Frameworks", frameworks),
        ("Databases", databases),
        ("DevOps/CI", devops),
        ("Cloud", cloud),
        "",
        ("Current Focus", focus),
        ("Location", stats.get("location", "India")),
        "",
        ("GitHub Stats", ""),
        ("  Repositories", str(stats.get("public_repos", 0))),
        ("  Followers", str(stats.get("followers", 0))),
        ("  Following", str(stats.get("following", 0))),
        ("  Commits", str(stats.get("total_commits", "0"))),
        ("  Stars Earned", str(stats.get("stars_earned", 0))),
        ("  Pull Requests", str(stats.get("total_prs", "0"))),
        ("  Issues/Reviews", f"{stats.get('total_issues', '0')} / {stats.get('total_reviews', '0')}")
    ]
    return lines

def generate_text_card(ascii_lines, neofetch_lines):
    """Generates a text-based stacked terminal layout."""
    card_lines = list(ascii_lines)
    card_lines.append("")
    card_lines.append("=" * 80)
    card_lines.append("")
    
    # Process neofetch lines into strings
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            card_lines.append(f"{k}: {v}")
        elif line == "":
            card_lines.append("")
        else:
            card_lines.append(line)
            
    return "\n".join(card_lines)

def generate_svg_card(ascii_lines, neofetch_lines):
    """Generates a premium, responsive SVG representing the Linux Terminal Card in a stacked layout."""
    # Settings
    font_family = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, Courier, monospace"
    text_color = "#c9d1d9"
    key_color = "#58a6ff"  # Blue accent
    title_color = "#58a6ff"
    border_color = "#30363d"
    bg_color = "#0d1117"
    
    width = 850
    
    # 1. Split neofetch lines into left (system info) and right (tech stack + github stats)
    left_col = [
        "🖥️ SYSTEM INFORMATION",
        "========================="
    ]
    right_col = [
        "📊 DEVELOPMENT PROFILE",
        "========================="
    ]
    
    # Extract keys for Left Column
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            if k in ["OS", "Uptime (GitHub age)", "Shell", "Editor", "Location", "Current Focus"]:
                left_col.append(line)
        elif isinstance(line, str) and "@" in line:
            left_col.append(line)
            left_col.append("-" * len(line))
            
    # Extract keys for Right Column
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            if k in ["Languages", "Frameworks", "Databases", "DevOps/CI", "Cloud"]:
                right_col.append(line)
                
    # Add GitHub stats sub-items to Right Column
    github_added = False
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            if k.strip() in ["Repositories", "Followers", "Following", "Commits", "Stars Earned", "Pull Requests", "Issues/Reviews"]:
                if not github_added:
                    right_col.append("")
                    right_col.append("GitHub Stats:")
                    github_added = True
                right_col.append(line)
                
    # Height calculation
    ascii_line_height = 14
    num_ascii_lines = len(ascii_lines)
    ascii_height = num_ascii_lines * ascii_line_height
    
    stats_line_height = 18
    num_stats_lines = max(len(left_col), len(right_col))
    stats_height = num_stats_lines * stats_line_height
    
    top_margin = 55
    middle_separator = 30
    bottom_margin = 30
    height = top_margin + ascii_height + middle_separator + stats_height + bottom_margin
    
    # SVG Boilerplate
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .terminal {{ font-family: {font_family}; font-size: 11px; fill: {text_color}; }}')
    svg.append(f'    .stats-text {{ font-family: {font_family}; font-size: 13px; fill: {text_color}; }}')
    svg.append(f'    .key {{ fill: {key_color}; font-weight: bold; }}')
    svg.append(f'    .title {{ fill: {title_color}; font-weight: bold; }}')
    svg.append('    .control-dot { stroke-width: 0; }')
    svg.append('    .header-text { fill: #8b949e; font-size: 12px; font-weight: bold; }')
    svg.append('  </style>')
    
    # Window Shadow and Background
    svg.append(f'  <rect width="{width}" height="{height}" rx="10" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" />')
    
    # Terminal Title Bar
    svg.append('  <!-- Title Bar -->')
    svg.append('  <circle cx="25" cy="22" r="6" fill="#ff5f56" class="control-dot" />')
    svg.append('  <circle cx="45" cy="22" r="6" fill="#ffbd2e" class="control-dot" />')
    svg.append('  <circle cx="65" cy="22" r="6" fill="#27c93f" class="control-dot" />')
    svg.append(f'  <text x="{width // 2}" y="26" text-anchor="middle" class="stats-text header-text">ashuu1408@developer-os:~</text>')
    svg.append(f'  <line x1="0" y1="40" x2="{width}" y2="40" stroke="{border_color}" stroke-width="1.5" />')
    
    # Render ASCII Art (Stacked on top)
    svg.append('  <!-- ASCII Art Section -->')
    svg.append('  <text x="30" y="60" class="terminal" xml:space="preserve">')
    for i, line in enumerate(ascii_lines):
        escaped_line = html.escape(line)
        svg.append(f'    <tspan x="30" dy="{0 if i == 0 else 1.2}em">{escaped_line}</tspan>')
    svg.append('  </text>')
    
    # Middle Separator Line
    separator_y = top_margin + ascii_height + 15
    svg.append(f'  <line x1="20" y1="{separator_y}" x2="{width - 20}" y2="{separator_y}" stroke="{border_color}" stroke-width="1.5" />')
    
    # Left Column: System Info
    stats_start_y = separator_y + 30
    svg.append('  <!-- Left Column: System Info -->')
    svg.append(f'  <text x="35" y="{stats_start_y}" class="stats-text" xml:space="preserve">')
    first = True
    for line in left_col:
        dy_val = 0 if first else 1.2
        first = False
        
        if isinstance(line, tuple):
            k, v = line
            escaped_k = html.escape(k)
            escaped_v = html.escape(v)
            svg.append(f'    <tspan x="35" dy="{dy_val}em"><tspan class="key">{escaped_k}</tspan>: {escaped_v}</tspan>')
        else:
            escaped_line = html.escape(line)
            if escaped_line.startswith("🖥️") or escaped_line.startswith("="):
                svg.append(f'    <tspan x="35" dy="{dy_val}em" fill="#8b949e">{escaped_line}</tspan>')
            elif "@" in line:
                svg.append(f'    <tspan x="35" dy="{dy_val}em" class="title">{escaped_line}</tspan>')
            else:
                svg.append(f'    <tspan x="35" dy="{dy_val}em" fill="#8b949e">{escaped_line}</tspan>')
    svg.append('  </text>')
    
    # Right Column: Dev Stack & Github Stats (X=440)
    svg.append('  <!-- Right Column: Dev Stack & Stats -->')
    svg.append(f'  <text x="440" y="{stats_start_y}" class="stats-text" xml:space="preserve">')
    first = True
    for line in right_col:
        dy_val = 0 if first else 1.2
        first = False
        
        if isinstance(line, tuple):
            k, v = line
            escaped_k = html.escape(k)
            escaped_v = html.escape(v)
            if k.startswith("  "):
                svg.append(f'    <tspan x="440" dy="{dy_val}em"><tspan class="key" fill="#8b949e">{escaped_k}</tspan>: {escaped_v}</tspan>')
            else:
                svg.append(f'    <tspan x="440" dy="{dy_val}em"><tspan class="key">{escaped_k}</tspan>: {escaped_v}</tspan>')
        elif line == "":
            svg.append(f'    <tspan x="440" dy="{dy_val}em"> </tspan>')
        else:
            escaped_line = html.escape(line)
            if escaped_line.startswith("📊") or escaped_line.startswith("="):
                svg.append(f'    <tspan x="440" dy="{dy_val}em" fill="#8b949e">{escaped_line}</tspan>')
            else:
                svg.append(f'    <tspan x="440" dy="{dy_val}em" font-weight="bold" fill="#58a6ff">{escaped_line}</tspan>')
    svg.append('  </text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    config, stats = load_stats_and_config()
    ascii_lines = load_ascii_art()
    neofetch_lines = format_neofetch_lines(config, stats)
    
    # 1. Generate text terminal card
    text_card = generate_text_card(ascii_lines, neofetch_lines)
    text_card_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "terminal_card.txt")
    with open(text_card_path, "w") as f:
        f.write(text_card)
    print(f"Plain text terminal card saved to {text_card_path}")
    
    # 2. Generate SVG card
    svg_card = generate_svg_card(ascii_lines, neofetch_lines)
    svg_card_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "terminal.svg")
    with open(svg_card_path, "w") as f:
        f.write(svg_card)
    print(f"SVG terminal card saved to {svg_card_path}")

if __name__ == "__main__":
    main()
