from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# The deterministic random state required by the specs
RANDOM_STATE = 42

def determine_k(usable_count: int) -> int:
    """
    Deterministically choose K based on usable user count.
    """
    if usable_count < 2:
        return 0
    elif usable_count == 2:
        # At most 2. We'll use 2 if they are separable, but for simplicity
        # we will start K at 2. If they are exactly the same, K-means handles it
        # but the assignment will just be 0 and 1 or both 0 depending on init.
        return 2
    elif usable_count <= 5:
        return usable_count - 1
    else:
        # Bounded deterministic K for small/medium datasets without endlessly tuning
        return 3

def label_cluster(centroid: np.ndarray, feature_names: list[str]) -> str:
    """
    Create a deterministic observable label based on the cluster's centroid.
    """
    # Create a mapping of feature to mean value
    feature_means = dict(zip(feature_names, centroid))
    
    # Simple rule-based labeling based on observed behaviors
    if feature_means.get("average_engagement", 0) > 10:
        return "High-Engagement Participants"
    elif feature_means.get("event_count", 0) > 10:
        return "Frequent Participants"
    elif feature_means.get("platform_count", 0) > 1:
        return "Multi-Platform Participants"
    elif feature_means.get("mention_count", 0) > 5 or feature_means.get("hashtag_count", 0) > 5:
        return "High-Network Connectors"
    else:
        return "Low-Frequency Participants"

def cluster_users(user_features: dict[str, dict[str, float]]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """
    Cluster users based on their features.
    
    Args:
        user_features: dict mapping user_id -> feature_dict
        
    Returns:
        tuple of:
        - dict mapping user_id -> cluster_id
        - list of cohort summaries
    """
    usable_users = list(user_features.keys())
    num_users = len(usable_users)
    
    k = determine_k(num_users)
    
    if k == 0:
        return {}, []
        
    if num_users == 0:
        return {}, []

    # Prepare feature matrix
    # Fix a consistent feature ordering
    if not usable_users:
        return {}, []
        
    feature_names = sorted(user_features[usable_users[0]].keys())
    
    X = []
    for uid in usable_users:
        row = [user_features[uid][fn] for fn in feature_names]
        X.append(row)
        
    X_array = np.array(X)
    
    # Handle the case where all usable users are identical
    # Standard scaler will complain/zero out, but we check if variance is 0
    if np.all(X_array == X_array[0]):
        # All users identical, collapse to K=1
        k = 1

    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_array)
    
    # Cluster
    kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    
    user_clusters = {uid: int(labels[i]) for i, uid in enumerate(usable_users)}
    
    # Build cohort summaries
    cohorts = []
    for cluster_id in range(k):
        # Users in this cluster
        cluster_user_ids = [uid for uid, cid in user_clusters.items() if cid == cluster_id]
        if not cluster_user_ids:
            continue
            
        centroid = kmeans.cluster_centers_[cluster_id]
        original_centroid = scaler.inverse_transform([centroid])[0]
        
        cohort_label = label_cluster(original_centroid, feature_names)
        
        # Aggregate stats
        total_events = sum(user_features[uid].get("event_count", 0) for uid in cluster_user_ids)
        avg_engagement = np.mean([user_features[uid].get("average_engagement", 0) for uid in cluster_user_ids])
        
        cohorts.append({
            "cohort_id": f"cohort_{cluster_id}",
            "label": cohort_label,
            "user_count": len(cluster_user_ids),
            "total_events": int(total_events),
            "average_engagement": float(avg_engagement),
            "confidence": 0.85 if len(cluster_user_ids) > 5 else 0.5, # Simple deterministic confidence
            "demographics": "insufficient data" # Enforced by requirements
        })
        
    return user_clusters, cohorts
