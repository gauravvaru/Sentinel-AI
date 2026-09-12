from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.insights.engine import InsightEngine
from src.insights.models import (
    AudienceEvidence,
    InsightEvidence,
    NetworkEvidence,
    SentimentEvidence,
    TrendEvidence,
)
from src.insights.reporter import InsightReporter


@pytest.fixture
def test_client():
    return TestClient(app)

def test_deterministic_reporter_all_insufficient():
    reporter = InsightReporter(use_llm=False)
    evidence = InsightEvidence(
        time_window_hours=24,
        data_quality="insufficient",
        sentiment=SentimentEvidence(available=False),
        trends=TrendEvidence(available=False),
        audience=AudienceEvidence(available=False),
        network=NetworkEvidence(available=False),
        limitations=["Testing limitation"]
    )
    
    report = reporter.generate_report(evidence)
    assert report.data_quality == "insufficient"
    assert "Insufficient Data" in report.headline
    assert len(report.key_findings) > 0
    assert "Testing limitation" in report.caveats
    assert report.evidence.audience.available is False

def test_deterministic_reporter_partial_data():
    reporter = InsightReporter(use_llm=False)
    evidence = InsightEvidence(
        time_window_hours=24,
        data_quality="moderate",
        sentiment=SentimentEvidence(available=False),
        trends=TrendEvidence(
            available=True, trending_topics_count=1, 
            top_topics=[{"name": "Tech"}]
        ),
        audience=AudienceEvidence(
            available=True, total_users_analyzed=100,
            usable_users=5, cohort_count=2
        ),
        network=NetworkEvidence(available=False),
        limitations=[]
    )
    
    report = reporter.generate_report(evidence)
    assert "Tech" in report.headline
    assert report.data_quality == "moderate"
    
    # Numeric grounding: ensuring 100 and 5 appear in key findings
    finding_texts = " ".join(report.key_findings)
    assert "1" in finding_texts
    assert "100" in finding_texts
    assert "5" in finding_texts
    assert "2" in finding_texts

@pytest.mark.asyncio
async def test_insight_engine_insufficient():
    session = AsyncMock()
    # Mock return values for DB queries to simulate empty database
    session.execute.return_value.scalars.return_value.all.return_value = []
    
    engine = InsightEngine(session)
    # Patch the components if needed, or let them naturally return empty lists if passed empty db results
    with (
        patch("src.insights.engine.TrendAnalysisService.get_topic_trend", return_value={"trend_score": 0, "metrics": {}}),
        patch("src.insights.engine.NetworkAnalyzer._fetch_events", return_value=[])
    ):
        evidence = await engine.gather_evidence()
        
        assert evidence.data_quality == "insufficient"
        assert not evidence.trends.available
        assert evidence.network.available
        assert evidence.network.node_count == 0
        assert not evidence.audience.available
        assert "Sentiment analytics are missing." in evidence.limitations

def test_api_insights_endpoint_empty_db(test_client):
    # Depending on DB state, this may return empty or partial
    # We just ensure it returns 200 and has the structure
    # Since TestClient works over a separate loop in async setups sometimes,
    # we patch the engine to just return a dummy evidence for safety in unit tests
    
    dummy_evidence = InsightEvidence(
        time_window_hours=24,
        data_quality="insufficient",
        sentiment=SentimentEvidence(),
        trends=TrendEvidence(),
        audience=AudienceEvidence(),
        network=NetworkEvidence()
    )
    
    with patch("src.api.insights.InsightEngine.gather_evidence", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = dummy_evidence
        
        response = test_client.get("/api/insights?time_window_hours=24")
        assert response.status_code == 200
        data = response.json()
        
        assert "headline" in data
        assert "summary" in data
        assert "key_findings" in data
        assert data["data_quality"] == "insufficient"
        assert not data["evidence"]["sentiment"]["available"]
