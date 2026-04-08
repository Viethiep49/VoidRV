"""
POST /api/v1/analyze — Demo mode: nhập tay text + sao → content score only.
Không lưu DB. Dùng để demo model cho thầy.
"""

from fastapi import APIRouter
from ..models.schemas import AnalyzeRequest, AnalyzeResponse
from ..services.content_module import analyze_content
from ..services.trust_engine import build_trust_result, get_badge, BADGE_LABELS, BADGE_COLORS
from ..ml.model import get_classifier

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_review(request: AnalyzeRequest):
    """
    Phân tích 1 review theo mode demo (không cần reviewer data).
    Chỉ tính Content Score. Behavior Score = N/A.
    """
    classifier = get_classifier()

    content_result = analyze_content(
        text=request.content,
        star_rating=request.star_rating,
        classifier=classifier,
        batch_texts=None,  # Không có batch — demo mode
    )

    trust = build_trust_result(content_result, behavior=None)

    return AnalyzeResponse(
        trust_score=trust.trust_score,
        confidence=trust.confidence,
        badge=trust.badge,
        badge_label=trust.badge_label,
        badge_color=trust.badge_color,
        content_only=True,
        caveat="Điểm này chỉ dựa trên nội dung review. Không có dữ liệu về người viết.",
        breakdown=trust.breakdown,
        aspects_found=trust.aspects_found,
        explanation=trust.explanation,
    )
