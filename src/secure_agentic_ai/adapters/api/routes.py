from typing import Annotated

from fastapi import APIRouter, Depends

from secure_agentic_ai.adapters.api.dependencies import get_request_action_use_case
from secure_agentic_ai.adapters.api.schemas import (
    HealthResponse,
    RequestActionPayload,
    RequestActionResponse,
)
from secure_agentic_ai.application.use_cases import RequestActionUseCase

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/actions", response_model=RequestActionResponse)
async def request_action(
    payload: RequestActionPayload,
    use_case: Annotated[RequestActionUseCase, Depends(get_request_action_use_case)],
) -> RequestActionResponse:
    command = payload.to_command()
    result = await use_case.execute(command)
    return RequestActionResponse.from_result(result)
