from __future__ import annotations

from dataclasses import dataclass

import praw

from axe_coo.models import RedditPost


@dataclass
class RedditResult:
    posts: list[RedditPost]
    used_creds: bool


def fetch_reddit_posts(
    ticker: str,
    client_id: str | None,
    client_secret: str | None,
    user_agent: str | None,
    subreddits: list[str] | None = None,
    limit: int = 25,
) -> RedditResult:
    if not (client_id and client_secret and user_agent):
        return RedditResult(posts=[], used_creds=False)

    subs = subreddits or ["wallstreetbets", "investing"]
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    out: list[RedditPost] = []
    q = ticker.upper()
    for sub in subs:
        try:
            for p in reddit.subreddit(sub).search(q, sort="new", limit=limit):
                out.append(
                    RedditPost(
                        subreddit=sub,
                        id=p.id,
                        title=p.title,
                        url=getattr(p, "url", None),
                        created_utc=getattr(p, "created_utc", None),
                        score=getattr(p, "score", None),
                        num_comments=getattr(p, "num_comments", None),
                        author=str(getattr(p, "author", "")) if getattr(p, "author", None) else None,
                    )
                )
        except Exception:
            continue

    return RedditResult(posts=out[: limit * len(subs)], used_creds=True)
