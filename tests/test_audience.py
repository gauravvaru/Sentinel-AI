from src.audience.clustering import cluster_users, determine_k
from src.audience.features import extract_user_features, is_usable_for_clustering


def test_extract_user_features():
    events = [
        {"likes": 5, "replies": 1, "shares": 2, "mentions": ["a"], "hashtags": ["#b"]},
        {"likes": 2, "replies": 0, "shares": 0, "platform": "twitter", "event_time": None}
    ]
    
    features = extract_user_features(events)
    
    assert features["event_count"] == 2.0
    assert features["total_likes"] == 7.0
    assert features["total_replies"] == 1.0
    assert features["total_shares"] == 2.0
    assert features["mention_count"] == 1.0
    assert features["hashtag_count"] == 1.0
    assert features["platform_count"] == 1.0
    assert features["average_engagement"] == 5.0 # (7+1+2)/2 = 10/2 = 5.0

def test_is_usable_for_clustering_single_event():
    # Even if they have lots of engagement, a single event is insufficient for behavioral patterns
    events = [{"likes": 100, "replies": 50, "shares": 10}]
    features = extract_user_features(events)
    assert not is_usable_for_clustering(features)

def test_is_usable_for_clustering_no_engagement():
    # 2 events but zero engagement is insufficient
    events = [
        {"likes": 0, "replies": 0, "shares": 0},
        {"likes": 0, "replies": 0, "shares": 0}
    ]
    features = extract_user_features(events)
    assert not is_usable_for_clustering(features)

def test_is_usable_for_clustering_success():
    # 2 events with some engagement is usable
    events = [
        {"likes": 1, "replies": 0, "shares": 0},
        {"likes": 0, "replies": 0, "shares": 0}
    ]
    features = extract_user_features(events)
    assert is_usable_for_clustering(features)
    
    # 3 events with 0 engagement is usable
    events2 = [
        {"likes": 0}, {"likes": 0}, {"likes": 0}
    ]
    assert is_usable_for_clustering(extract_user_features(events2))

def test_determine_k():
    assert determine_k(0) == 0
    assert determine_k(1) == 0
    assert determine_k(2) == 2
    assert determine_k(3) == 2
    assert determine_k(4) == 3
    assert determine_k(5) == 4
    assert determine_k(6) == 3 # Bounded

def test_cluster_users_empty():
    user_clusters, cohorts = cluster_users({})
    assert len(user_clusters) == 0
    assert len(cohorts) == 0

def test_cluster_users_one():
    features = {"user1": {"event_count": 5, "average_engagement": 10}}
    user_clusters, cohorts = cluster_users(features)
    assert len(user_clusters) == 0
    assert len(cohorts) == 0

def test_cluster_users_identical():
    features = {
        "user1": {"event_count": 5, "average_engagement": 10},
        "user2": {"event_count": 5, "average_engagement": 10}
    }
    user_clusters, cohorts = cluster_users(features)
    assert len(user_clusters) == 2
    assert len(cohorts) == 1
    assert cohorts[0]["user_count"] == 2

def test_cluster_users_distinct():
    features = {
        "user1": {"event_count": 1, "average_engagement": 0},
        "user2": {"event_count": 20, "average_engagement": 50},
        "user3": {"event_count": 1, "average_engagement": 1}
    }
    # Should cluster user1 & user3 together, user2 separately
    user_clusters, cohorts = cluster_users(features)
    assert len(user_clusters) == 3
    assert len(cohorts) <= 2
    
    # Test labels don't contain demographic guesses
    for c in cohorts:
        assert c["demographics"] == "insufficient data"
        assert c["label"] in ["High-Engagement Participants", "Frequent Participants", "Multi-Platform Participants", "High-Network Connectors", "Low-Frequency Participants"]
