from src.insights.models import InsightEvidence, InsightResponse


class InsightReporter:
    """
    A reporting layer over the structured analytics evidence.
    This class handles the conversion of deterministic evidence into a structured response.
    It acts as a fallback or a provider-agnostic LLM interface.
    """
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        
    def generate_report(self, evidence: InsightEvidence) -> InsightResponse:
        """
        Generates the final insight report.
        If an LLM were configured, it would be passed the evidence dict here
        with strict instructions to NOT invent numbers.
        Since no LLM provider is configured, we use the deterministic fallback.
        """
        # Deterministic generation
        
        # 1. Headline
        headline = "System Status Report"
        if evidence.data_quality in ["high", "moderate"]:
            if evidence.trends.available and evidence.trends.trending_topics_count > 0:
                top_topic = evidence.trends.top_topics[0].get("name", "Unknown Topic")
                headline = f"Analysis: Engagement detected around '{top_topic}'"
            elif evidence.network.available and evidence.network.node_count > 0:
                headline = f"Analysis: Active network detected with {evidence.network.node_count} nodes"
        elif evidence.data_quality == "low":
            headline = "Partial Analysis: Limited data signals"
        else:
            headline = "Insufficient Data for meaningful analysis"
            
        # 2. Summary & Key Findings
        key_findings = []
        summary = "Based on available evidence, "
        
        if evidence.data_quality == "insufficient":
            summary += "there is currently insufficient data across modules to provide a robust insight."
            key_findings.append("Data volume is below the threshold for reliable extraction.")
        else:
            summary += f"the system extracted signals across {evidence.time_window_hours} hours."
            
            if evidence.trends.available and evidence.trends.trending_topics_count > 0:
                key_findings.append(f"Trending: {evidence.trends.trending_topics_count} topic(s) show momentum.")
            
            if evidence.network.available and evidence.network.node_count > 0:
                kf = f"Network: {evidence.network.node_count} participants observed with {evidence.network.edge_count} interactions."
                if evidence.network.community_count > 0:
                    kf += f" Detected {evidence.network.community_count} distinct groupings."
                key_findings.append(kf)
                
            if evidence.audience.available:
                if evidence.audience.usable_users > 0:
                    kf = f"Audience: {evidence.audience.usable_users} users out of {evidence.audience.total_users_analyzed} analyzed had sufficient engagement for behavioral profiling."
                    if evidence.audience.cohort_count > 0:
                        kf += f" Resulting in {evidence.audience.cohort_count} observable cohorts."
                    key_findings.append(kf)
                else:
                    key_findings.append(f"Audience: Insufficient behavioral data among {evidence.audience.total_users_analyzed} users.")
                    
            if evidence.sentiment.available:
                pass # Currently not available
            else:
                key_findings.append("Sentiment: Unavailable in current production pipeline.")

        return InsightResponse(
            headline=headline,
            summary=summary,
            key_findings=key_findings,
            evidence=evidence,
            caveats=evidence.limitations,
            data_quality=evidence.data_quality
        )
