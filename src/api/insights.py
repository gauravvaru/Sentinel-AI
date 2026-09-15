
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.insights.engine import InsightEngine
from src.insights.models import InsightResponse
from src.insights.reporter import InsightReporter

insights_router = APIRouter()

from src.utils.cache import ttl_cache

@insights_router.get("/api/insights", response_model=InsightResponse)
@ttl_cache(ttl_seconds=60)
async def get_insights(
    time_window_hours: int = Query(24, description="Time window in hours for cross-module analytics"),
    topic_id: int | None = Query(None, description="Optional topic filter (currently unapplied to preserve global state)"),
    session: AsyncSession = Depends(get_session)  # noqa: B008
):
    """
    Returns a structured insight report powered by the Insights Engine.
    All numeric values are backed by persisted structured analytics.
    """
    engine = InsightEngine(session)
    # Fetch structural evidence securely
    evidence = await engine.gather_evidence(time_window_hours=time_window_hours)
    
    reporter = InsightReporter(use_llm=False)
    report = reporter.generate_report(evidence)
    
    return report
