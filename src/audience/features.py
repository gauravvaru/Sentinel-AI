from typing import Any


def extract_user_features(events: list[dict[str, Any]]) -> dict[str, float]:
    """
    Extract deterministic aggregate behavioral metrics for a user from their events.
    """
    if not events:
        return {}

    event_count = len(events)
    total_likes = 0
    total_replies = 0
    total_shares = 0
    mention_count = 0
    hashtag_count = 0
    platforms = set()
    active_days = set()

    for event in events:
        total_likes += event.get("likes") or 0
        total_replies += event.get("replies") or 0
        total_shares += event.get("shares") or 0
        
        mentions = event.get("mentions") or []
        hashtag = event.get("hashtags") or []
        mention_count += len(mentions)
        hashtag_count += len(hashtag)
        
        if event.get("platform"):
            platforms.add(event.get("platform"))
            
        event_time = event.get("event_time")
        if event_time:
            # Assuming datetime object
            active_days.add(event_time.date())

    return {
        "event_count": float(event_count),
        "total_likes": float(total_likes),
        "total_replies": float(total_replies),
        "total_shares": float(total_shares),
        "mention_count": float(mention_count),
        "hashtag_count": float(hashtag_count),
        "platform_count": float(len(platforms)),
        "active_days": float(len(active_days)),
        "average_engagement": float(total_likes + total_replies + total_shares) / event_count if event_count > 0 else 0.0
    }

def is_usable_for_clustering(features: dict[str, float]) -> bool:
    """
    Determine if a user has sufficient evidence to be clustered.
    
    Data sufficiency policy:
    1. A single event is NEVER sufficient (even with hashtags/mentions).
    2. event_count >= 2 requires some observable engagement.
    3. Users meeting minimums are considered "usable".
    """
    if not features:
        return False
        
    event_count = features.get("event_count", 0.0)
    engagement = features.get("total_likes", 0.0) + features.get("total_replies", 0.0) + features.get("total_shares", 0.0)
    
    if event_count < 2.0:
        return False
        
    # If they only posted twice and got absolute zero engagement, not enough behavioral signal
    return not (event_count == 2.0 and engagement == 0.0)
