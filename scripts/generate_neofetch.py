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
    """Generates a text-based side-by-side terminal layout."""
    card_lines = []
    
    # Find max width of ASCII lines to pad them properly
    max_ascii_w = max(len(l) for l in ascii_lines) if ascii_lines else 20
    
    # Process neofetch lines into strings
    formatted_stats = []
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            formatted_stats.append(f"\033[38;5;75m{k}\033[0m: {v}")
        elif line == "":
            formatted_stats.append("")
        else:
            # Highlight title header
            if "@" in line:
                formatted_stats.append(f"\033[1;38;5;81m{line}\033[0m")
            else:
                formatted_stats.append(line)
                
    # Plain text version for README markdown (without ANSI color codes since GitHub strips them)
    plain_stats = []
    for line in neofetch_lines:
        if isinstance(line, tuple):
            k, v = line
            # Check if it's subhead
            if k.startswith("  "):
                plain_stats.append(f"{k}: {v}")
            else:
                plain_stats.append(f"{k}: {v}")
        else:
            plain_stats.append(line)
            
    # Combine side-by-side
    num_lines = max(len(ascii_lines), len(plain_stats))
    for i in range(num_lines):
        a_line = ascii_lines[i] if i < len(ascii_lines) else ""
        s_line = plain_stats[i] if i < len(plain_stats) else ""
        
        # Pad ASCII line to max width
        a_padded = a_line.ljust(max_ascii_w)
        card_lines.append(f"{a_padded}   {s_line}")
        
    return "\n".join(card_lines)

def generate_svg_card(ascii_lines, neofetch_lines):
    """Generates a premium, responsive SVG representing the Linux Terminal Card."""
    # Settings
    font_family = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, Courier, monospace"
    text_color = "#c9d1d9"
    key_color = "#58a6ff"  # Blue accent
    title_color = "#58a6ff"
    border_color = "#30363d"
    bg_color = "#0d1117"
    
    width = 850
    # Determine height based on lines
    num_lines = max(len(ascii_lines), len(neofetch_lines))
    line_height = 18
    top_margin = 55
    bottom_margin = 25
    height = top_margin + (num_lines * line_height) + bottom_margin
    
    # SVG Boilerplate
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .terminal {{ font-family: {font_family}; font-size: 13px; fill: {text_color}; }}')
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
    svg.append(f'  <text x="{width // 2}" y="26" text-anchor="middle" class="terminal header-text">ashuu1408@developer-os:~</text>')
    svg.append(f'  <line x1="0" y1="40" x2="{width}" y2="40" stroke="{border_color}" stroke-width="1.5" />')
    
    # Left Column: ASCII Art
    svg.append('  <!-- ASCII Art Column -->')
    svg.append('  <text x="25" y="60" class="terminal" xml:space="preserve">')
    for i, line in enumerate(ascii_lines):
        escaped_line = html.escape(line)
        svg.append(f'    <tspan x="25" dy="{0 if i == 0 else 1.2}em">{escaped_line}</tspan>')
    svg.append('  </text>')
    
    # Right Column: Neofetch Stats
    svg.append('  <!-- Neofetch Stats Column -->')
    # Place right column at X=410
    svg.append('  <text x="410" y="60" class="terminal" xml:space="preserve">')
    
    first = True
    for line in neofetch_lines:
        dy_val = 0 if first else 1.2
        first = False
        
        if isinstance(line, tuple):
            k, v = line
            escaped_k = html.escape(k)
            escaped_v = html.escape(v)
            # Differentiate main keys and stats indented keys
            if k.startswith("  "):
                svg.append(f'    <tspan x="410" dy="{dy_val}em"><tspan class="key" fill="#888">{escaped_k}</tspan>: {escaped_v}</tspan>')
            else:
                svg.append(f'    <tspan x="410" dy="{dy_val}em"><tspan class="key">{escaped_k}</tspan>: {escaped_v}</tspan>')
        elif line == "":
            svg.append(f'    <tspan x="410" dy="{dy_val}em"> </tspan>')
        else:
            escaped_line = html.escape(line)
            if "@" in line:
                svg.append(f'    <tspan x="410" dy="{dy_val}em" class="title">{escaped_line}</tspan>')
            elif "-" in line and all(c == '-' for c in line.strip()):
                svg.append(f'    <tspan x="410" dy="{dy_val}em" fill="#30363d">{escaped_line}</tspan>')
            else:
                svg.append(f'    <tspan x="410" dy="{dy_val}em" font-weight="bold" fill="#58a6ff">{escaped_line}</tspan>')
                
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
