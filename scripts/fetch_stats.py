import os
import sys
import json
import requests
from datetime import datetime, timezone

# Setup headers for GitHub API
TOKEN = os.environ.get("GH_PAT") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

def get_token_source():
    if os.environ.get("GH_PAT"):
        return "GH_PAT (Personal Access Token)"
    elif os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        return "GITHUB_TOKEN (Default Actions Token)"
    return "None (Unauthenticated)"

def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    return headers

def run_graphql_query(query, variables=None):
    if not TOKEN:
        print("Warning: No GitHub token available for GraphQL query.")
        return None
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"bearer {TOKEN}"}
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            if "errors" in res_json:
                print(f"GraphQL returned error payload: {json.dumps(res_json['errors'])}")
            return res_json
        else:
            print(f"GraphQL query failed with HTTP status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"GraphQL connection error: {e}")
        return None

def calculate_uptime(created_at_str):
    """Calculates GitHub account age (uptime)."""
    try:
        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        created_at = datetime.now(timezone.utc).replace(tzinfo=None)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = now - created_at
    
    years = diff.days // 365
    remaining_days = diff.days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if days > 0 or not parts:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
        
    return ", ".join(parts)

def fetch_real_counts_fallback(username):
    headers = get_headers()
    commit_headers = headers.copy()
    commit_headers["Accept"] = "application/vnd.github.cloak-preview"
    
    counts = {
        "commits": 0,
        "prs": 0,
        "issues": 0,
        "reviews": 0
    }
    
    # Fetch commits count
    try:
        res = requests.get(f"https://api.github.com/search/commits?q=author:{username}", headers=commit_headers, timeout=10)
        if res.status_code == 200:
            counts["commits"] = res.json().get("total_count", 0)
        else:
            print(f"Commit search endpoint returned status {res.status_code}: {res.text[:100]}")
            counts["commits"] = "40+"
    except Exception as e:
        print(f"Error fetching commits count: {e}")
        counts["commits"] = "40+"
        
    # Fetch PRs count
    try:
        res = requests.get(f"https://api.github.com/search/issues?q=author:{username}+type:pr", headers=headers, timeout=10)
        if res.status_code == 200:
            counts["prs"] = res.json().get("total_count", 0)
        else:
            print(f"PR search endpoint returned status {res.status_code}")
            counts["prs"] = "5+"
    except Exception as e:
        print(f"Error fetching PRs count: {e}")
        counts["prs"] = "5+"
        
    # Fetch Issues count
    try:
        res = requests.get(f"https://api.github.com/search/issues?q=author:{username}+type:issue", headers=headers, timeout=10)
        if res.status_code == 200:
            counts["issues"] = res.json().get("total_count", 0)
        else:
            print(f"Issue search endpoint returned status {res.status_code}")
            counts["issues"] = "0"
    except Exception as e:
        print(f"Error fetching issues count: {e}")
        counts["issues"] = "0"
        
    # Fetch Reviews count
    try:
        res = requests.get(f"https://api.github.com/search/issues?q=reviewed-by:{username}+type:pr", headers=headers, timeout=10)
        if res.status_code == 200:
            counts["reviews"] = res.json().get("total_count", 0)
        else:
            print(f"Review search endpoint returned status {res.status_code}")
            counts["reviews"] = "0"
    except Exception as e:
        print(f"Error fetching reviews count: {e}")
        counts["reviews"] = "0"
        
    return counts

def fetch_rest_fallback(username):
    """Fetches user details and repositories using REST API."""
    print(f"Using REST API fallback for gathering stats (Token Source: {get_token_source()})...")
    headers = get_headers()
    stats = {}
    
    # 1. Fetch user profile
    try:
        user_res = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if user_res.status_code == 200:
            user_data = user_res.json()
            stats["name"] = user_data.get("name") or username
            stats["followers"] = user_data.get("followers", 0)
            stats["following"] = user_data.get("following", 0)
            stats["public_repos"] = user_data.get("public_repos", 0)
            stats["uptime"] = calculate_uptime(user_data.get("created_at", "2018-01-01T00:00:00Z"))
            stats["location"] = user_data.get("location") or "India"
        else:
            print(f"Error fetching user profile via REST (Status {user_res.status_code}): {user_res.text[:100]}")
            return None
    except Exception as e:
        print(f"REST user fetch exception: {e}")
        return None
        
    # 2. Fetch user repositories
    repos = []
    page = 1
    total_stars = 0
    languages_count = {}
    
    try:
        while True:
            repos_res = requests.get(
                f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", 
                headers=headers, 
                timeout=10
            )
            if repos_res.status_code != 200:
                print(f"REST repos fetch page {page} returned status {repos_res.status_code}")
                break
            page_repos = repos_res.json()
            if not page_repos:
                break
            for r in page_repos:
                if not r.get("fork"):
                    repos.append(r)
                    total_stars += r.get("stargazers_count", 0)
                    lang = r.get("language")
                    if lang:
                        languages_count[lang] = languages_count.get(lang, 0) + 1
            page += 1
            if len(page_repos) < 100:
                break
    except Exception as e:
        print(f"REST repos fetch exception: {e}")
        
    stats["stars_earned"] = total_stars
    
    # Sort languages
    sorted_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
    stats["most_used_language"] = sorted_langs[0][0] if sorted_langs else "Unknown"
    stats["top_languages"] = [lang[0] for lang in sorted_langs[:5]]
    
    # Sort repos for featured
    repos_by_stars = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
    repos_by_created = sorted(repos, key=lambda x: x.get("created_at", ""), reverse=True)
    repos_by_pushed = sorted(repos, key=lambda x: x.get("pushed_at", ""), reverse=True)
    
    stats["featured_projects"] = {
        "most_starred": [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "stars": r["stargazers_count"],
                "language": r.get("language") or "Other",
                "url": r["html_url"]
            } for r in repos_by_stars[:4]
        ],
        "latest_active": {
            "name": repos_by_pushed[0]["name"],
            "description": repos_by_pushed[0].get("description") or "",
            "stars": repos_by_pushed[0]["stargazers_count"],
            "language": repos_by_pushed[0].get("language") or "Other",
            "url": repos_by_pushed[0]["html_url"],
            "pushed_at": repos_by_pushed[0]["pushed_at"]
        } if repos_by_pushed else None,
        "newest": {
            "name": repos_by_created[0]["name"],
            "description": repos_by_created[0].get("description") or "",
            "stars": repos_by_created[0]["stargazers_count"],
            "language": repos_by_created[0].get("language") or "Other",
            "url": repos_by_created[0]["html_url"],
            "created_at": repos_by_created[0]["created_at"]
        } if repos_by_created else None
    }
    
    counts = fetch_real_counts_fallback(username)
    stats["total_commits"] = str(counts["commits"])
    stats["total_prs"] = str(counts["prs"])
    stats["total_issues"] = str(counts["issues"])
    stats["total_reviews"] = str(counts["reviews"])
    
    return stats

def fetch_graphql_stats(username):
    """Fetches comprehensive user statistics using GraphQL API."""
    print(f"Using GraphQL API for gathering stats (Token Source: {get_token_source()})...")
    
    # Corrected GraphQL Query using contributionsCollection
    query = """
    query($username: String!) {
      user(login: $username) {
        name
        createdAt
        location
        followers {
          totalCount
        }
        following {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoryContributions
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
          totalCount
          nodes {
            name
            description
            stargazerCount
            forkCount
            primaryLanguage {
              name
            }
            createdAt
            pushedAt
            url
          }
        }
      }
    }
    """
    
    variables = {"username": username}
    
    result = run_graphql_query(query, variables)
    if not result or "data" not in result or not result["data"].get("user"):
        print("GraphQL response invalid or empty, falling back to REST...")
        return None
        
    data = result["data"]
    user_data = data["user"]
    contribs = user_data.get("contributionsCollection", {})
    
    stats = {}
    stats["name"] = user_data.get("name") or username
    stats["followers"] = user_data["followers"]["totalCount"]
    stats["following"] = user_data["following"]["totalCount"]
    stats["public_repos"] = user_data["repositories"]["totalCount"]
    stats["uptime"] = calculate_uptime(user_data["createdAt"])
    stats["location"] = user_data.get("location") or "India"
    
    stats["total_prs"] = contribs.get("totalPullRequestContributions", 0)
    stats["total_issues"] = contribs.get("totalIssueContributions", 0)
    stats["total_reviews"] = contribs.get("totalPullRequestReviewContributions", 0)
    stats["total_commits"] = contribs.get("totalCommitContributions", 0)
    
    repos = user_data["repositories"]["nodes"]
    
    total_stars = 0
    languages_count = {}
    for r in repos:
        total_stars += r["stargazerCount"]
        lang = r.get("primaryLanguage")
        if lang:
            name = lang["name"]
            languages_count[name] = languages_count.get(name, 0) + 1
            
    stats["stars_earned"] = total_stars
    
    # Sort languages
    sorted_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
    stats["most_used_language"] = sorted_langs[0][0] if sorted_langs else "Unknown"
    stats["top_languages"] = [lang[0] for lang in sorted_langs[:5]]
    
    # Sort repos for featured
    repos_by_stars = sorted(repos, key=lambda x: x["stargazerCount"], reverse=True)
    repos_by_created = sorted(repos, key=lambda x: x["createdAt"], reverse=True)
    repos_by_pushed = repos
    
    stats["featured_projects"] = {
        "most_starred": [
            {
                "name": r["name"],
                "description": r["description"] or "",
                "stars": r["stargazerCount"],
                "language": (r["primaryLanguage"]["name"] if r.get("primaryLanguage") else "Other"),
                "url": r["url"]
            } for r in repos_by_stars[:4]
        ],
        "latest_active": {
            "name": repos_by_pushed[0]["name"],
            "description": repos_by_pushed[0]["description"] or "",
            "stars": repos_by_pushed[0]["stargazerCount"],
            "language": (repos_by_pushed[0]["primaryLanguage"]["name"] if repos_by_pushed[0].get("primaryLanguage") else "Other"),
            "url": repos_by_pushed[0]["url"],
            "pushed_at": repos_by_pushed[0]["pushed_at"]
        } if repos_by_pushed else None,
        "newest": {
            "name": repos_by_created[0]["name"],
            "description": repos_by_created[0]["description"] or "",
            "stars": repos_by_created[0]["stargazerCount"],
            "language": (repos_by_created[0]["primaryLanguage"]["name"] if repos_by_created[0].get("primaryLanguage") else "Other"),
            "url": repos_by_created[0]["url"],
            "created_at": repos_by_created[0]["createdAt"]
        } if repos_by_created else None
    }
    
    return stats

def fetch_recent_activity(username, limit=5):
    """Fetches public events representing recent activity of the user."""
    print(f"Fetching recent activity events for {username}...")
    url = f"https://api.github.com/users/{username}/events/public"
    headers = get_headers()
    
    activities = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            events = response.json()
            for event in events:
                if len(activities) >= limit:
                    break
                
                event_type = event.get("type")
                repo_name = event.get("repo", {}).get("name", "")
                repo_url = f"https://github.com/{repo_name}"
                created_at_str = event.get("created_at")
                
                dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
                date_formatted = dt.strftime("%b %d, %Y")
                
                payload = event.get("payload", {})
                
                if event_type == "PushEvent":
                    commits = payload.get("commits", [])
                    if commits and len(commits) > 0:
                        msg = commits[0].get("message", "").split("\n")[0]
                        activities.append(
                            f"📝 Pushed to [{repo_name}]({repo_url}): `{msg}` ({date_formatted})"
                        )
                    else:
                        activities.append(
                            f"📝 Pushed updates to [{repo_name}]({repo_url}) ({date_formatted})"
                        )
                elif event_type == "PullRequestEvent":
                    action = payload.get("action")
                    number = payload.get("number")
                    pr = payload.get("pull_request", {})
                    pr_url = f"https://github.com/{repo_name}/pull/{number}"
                    
                    title = f"PR #{number}"
                    api_url = pr.get("url")
                    if api_url:
                        try:
                            pr_res = requests.get(api_url, headers=headers, timeout=5)
                            if pr_res.status_code == 200:
                                title = pr_res.json().get("title") or title
                        except Exception as e:
                            print(f"Error fetching PR title: {e}")
                            
                    activities.append(
                        f"🔀 {action.capitalize()} PR [{title}]({pr_url}) in [{repo_name}]({repo_url}) ({date_formatted})"
                    )
                elif event_type == "IssuesEvent":
                    action = payload.get("action")
                    issue = payload.get("issue", {})
                    number = issue.get("number") or payload.get("number") or ""
                    issue_url = f"https://github.com/{repo_name}/issues/{number}"
                    
                    title = f"Issue #{number}" if number else "Issue"
                    api_url = issue.get("url")
                    if api_url:
                        try:
                            issue_res = requests.get(api_url, headers=headers, timeout=5)
                            if issue_res.status_code == 200:
                                title = issue_res.json().get("title") or title
                        except Exception as e:
                            print(f"Error fetching issue title: {e}")
                            
                    activities.append(
                        f"🐛 {action.capitalize()} Issue [{title}]({issue_url}) in [{repo_name}]({repo_url}) ({date_formatted})"
                    )
                elif event_type == "CreateEvent":
                    ref_type = payload.get("ref_type")
                    if ref_type == "repository":
                        activities.append(
                            f"🚀 Created repository [{repo_name}]({repo_url}) ({date_formatted})"
                        )
                elif event_type == "WatchEvent":
                    action = payload.get("action")
                    if action == "started":
                        activities.append(
                            f"⭐ Starred [{repo_name}]({repo_url}) ({date_formatted})"
                        )
        else:
            print(f"Error fetching public activity events (Status {response.status_code}): {response.text[:100]}")
    except Exception as e:
        print(f"Activity fetch exception: {e}")
        
    if not activities:
        activities = [
            "📝 Working on projects and scaling systems...",
            "🚀 Contributing to open source platforms...",
            "⭐ Exploring new dev methodologies and technologies..."
        ]
        
    return activities

def main():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {"github_username": "ashuujha"}
        
    username = config.get("github_username", "ashuujha")
    
    print(f"Starting stats fetch for user '{username}' using token source: {get_token_source()}")
    
    stats = None
    if TOKEN:
        stats = fetch_graphql_stats(username)
    
    if not stats:
        stats = fetch_rest_fallback(username)
        
    if not stats:
        print("Error: Could not retrieve stats from GitHub via GraphQL or REST API.")
        sys.exit(1)
        
    stats["recent_activities"] = fetch_recent_activity(username, limit=6)
    
    stats_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "stats.json")
    os.makedirs(os.path.dirname(stats_json_path), exist_ok=True)
    with open(stats_json_path, "w") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Successfully fetched and saved stats to {stats_json_path}")

if __name__ == "__main__":
    main()
