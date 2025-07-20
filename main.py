import os
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
from typing import Any, Optional, List, Dict

mcp = FastMCP("works-mcp")
token = os.getenv("WORKS_API_TOKEN")

if not token:
    raise EnvironmentError("WORKS_API_TOKEN environment variable is not set")

headers = {
    "Authorization": f"Bearer {token}"
}

############## TASK ##############

@mcp.tool()
async def get_my_tasks(categoryId: str, count: int = 50, status: str = "TODO", searchFilterType: str = "ALL") -> Any:
    """
    Get the list of my tasks
    https://developers.worksmobile.com/kr/docs/user-task-list
    """
     # Validate count
    if not (0 <= count <= 100):
        raise ValueError("count must be between 0 and 100")

    # Validate status
    allowed_status = {"TODO", "ALL"}
    if status not in allowed_status:
        raise ValueError(f"status must be one of {allowed_status}")

    # Validate searchFilterType
    allowed_filter_types = {"ALL", "ASSIGNEE", "ASSIGNOR"}
    if searchFilterType not in allowed_filter_types:
        raise ValueError(f"searchFilterType must be one of {allowed_filter_types}")

    # Assuming you have an API endpoint that returns tasks for the user
    url = "https://www.worksapis.com/v1.0/users/me/tasks"
    query_params = {
        "categoryId": categoryId,
        "count": count,
        "status": status,
        "searchFilterType": searchFilterType
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, params=query_params)  # Pass query_params
        response.raise_for_status()
        return response.json()  # Parse and return the JSON response


    
@mcp.tool()
async def delete_my_task(taskId: str) -> Any:
    """
    Delete a task by its taskId
    https://developers.worksmobile.com/kr/docs/user-task-delete
    Args:
        taskId: The ID of the task to delete (required)
    Returns:
        dict: Result of the delete operation with status information
    """
    if not taskId:
        raise ValueError("taskId is required")

    url = f"https://www.worksapis.com/v1.0/tasks/{taskId}"
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.delete(url)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Task {taskId} deleted successfully",
            "status_code": response.status_code,
            "task_id": taskId
        }

@mcp.tool()
async def create_my_task(
    assignorId: str,
    assignees: list[dict[str, str]],  
    title: str,
    content: str,
    dueDate: Optional[str] = None,
    completionCondition: str = "ANY_ONE",
    categoryId: Optional[str] = None
) -> dict[str, Any]:  
    """
    Create a new task
    https://developers.worksmobile.com/kr/docs/user-task-create

    Args:
        assignorId: The ID of the assignor (required)
        assignees: List of assignees with their statuses (required)
        title: Title of the task (required)
        content: Content of the task (required)
        dueDate: Due date of the task (optional, format: YYYY-MM-DD)
        completionCondition: Completion condition (default: "ANY_ONE")
        categoryId: ID of the task category (optional)

    Returns:
        dict: Details of the created task

    Example:
        await create_my_task(
            assignorId="user123",
            assignees=[
                {"assigneeId": "user456", "status": "TODO"},
                {"assigneeId": "user789", "status": "TODO"}
            ],
            title="프로젝트 기획서 작성",
            content="Q1 프로젝트 기획서를 작성해주세요.",
            dueDate="2024-02-15",
            categoryId="category123"
        )
    """
    
    # Validate required fields
    if not assignorId or not assignorId.strip():
        raise ValueError("assignorId is required and cannot be empty")
    
    if not assignees or not isinstance(assignees, list):
        raise ValueError("assignees must be a non-empty list")
    
    if not title or not title.strip():
        raise ValueError("title is required and cannot be empty")
    
    if not content or not content.strip():
        raise ValueError("content is required and cannot be empty")
    
    if completionCondition not in {"ANY_ONE", "MUST_ALL"}:
        raise ValueError("completionCondition must be 'ANY_ONE' or 'MUST_ALL'")

    # Validate assignees
    for i, assignee in enumerate(assignees):
        if not isinstance(assignee, dict):
            raise ValueError(f"assignee at index {i} must be a dictionary")
        
        if "assigneeId" not in assignee or "status" not in assignee:
            raise ValueError(f"assignee at index {i} must have 'assigneeId' and 'status'")
        
        if not assignee["assigneeId"] or not assignee["assigneeId"].strip():
            raise ValueError(f"assignee at index {i} must have a valid assigneeId")
        
        if assignee["status"] not in {"TODO", "DONE"}:
            raise ValueError(f"assignee at index {i} 'status' must be 'TODO' or 'DONE'")

    # Validate dueDate format if provided
    if dueDate:
        try:
            datetime.strptime(dueDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError("dueDate must be in YYYY-MM-DD format")

    # API endpoint and headers
    url = "https://www.worksapis.com/v1.0/users/me/tasks"
    post_headers = headers.copy()
    post_headers["Content-Type"] = "application/json"
    
    # Request body
    request_body = {
        "assignorId": assignorId.strip(),
        "assignees": assignees,
        "title": title.strip(),
        "content": content.strip(),
        "completionCondition": completionCondition
    }
    
    if dueDate:
        request_body["dueDate"] = dueDate
    
    if categoryId and categoryId.strip():
        request_body["categoryId"] = categoryId.strip()

    
    async with httpx.AsyncClient(headers=post_headers) as client:
        response = await client.post(url, json=request_body)
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "message": "task가 성공적으로 생성되었습니다",
            "data": result,
            "status_code": response.status_code
        }


@mcp.tool()
async def get_my_categories() -> Any:
    """
    Get the list of my categories
    https://developers.worksmobile.com/kr/docs/user-task-category-list
    """
    url = "https://www.worksapis.com/v1.0/users/me/task-categories"
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()  # Parse the JSON response
        
        # Ensure the response contains the expected "taskCategories" key
        if "taskCategories" not in data:
            raise ValueError("Invalid response: 'taskCategories' key not found")
        
        return data["taskCategories"]  # Return only the task categories


@mcp.tool()
async def delete_my_category(categoryId: str) -> Any:
    """
    Delete a task category by its categoryId
    https://developers.worksmobile.com/kr/docs/user-task-category-delete
    Args:
        categoryId: The ID of the category to delete (required)
    Returns:
        dict: Result of the delete operation with status information
    """
    url = f"https://www.worksapis.com/v1.0/users/me/task-categories/{categoryId}"
    if not categoryId:
        raise ValueError("categoryId is required")

    async with httpx.AsyncClient(headers=headers) as client:
            response = await client.delete(url)
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"category {categoryId} deleted successfully",
                "status_code": response.status_code,
                "event_id": categoryId
            }



############# Event #############

@mcp.tool()
async def get_default_calendar_events(
    fromDateTime: str,
    untilDateTime: str
) -> Any:
    """
    Get the list of calendars
    기본 캘린더 일정 목록 조회
    https://developers.worksmobile.com/kr/docs/calendar-default-event-user-list

    Args:
        fromDateTime: Start datetime for event retrieval (required, format: YYYY-MM-DDThh:mm:ssTZD)
        untilDateTime: End datetime for event retrieval (required, format: YYYY-MM-DDThh:mm:ssTZD)
        # Encode "+" as "%2B"
    Returns:
        dict: List of calendar events
    """

        # Validate fromDateTime and untilDateTime
    if not fromDateTime or not untilDateTime:
        raise ValueError("Both fromDateTime and untilDateTime are required")
    
    url = f"https://www.worksapis.com/v1.0/users/me/calendar/events"
    query_params = {
        "fromDateTime": fromDateTime.replace("+", "%2B"),  
        "untilDateTime": untilDateTime.replace("+", "%2B")
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, params=query_params)
        response.raise_for_status()
        return response.json()



@mcp.tool()
async def create_default_calendar_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    timezone: str = "Asia/Seoul",
    description: Optional[str] = None,
    location: Optional[str] = None,
    event_id: Optional[str] = None,
    category_id: Optional[str] = None,
    attendees: Optional[List[Dict]] = None,
    visibility: str = "PUBLIC",
    transparency: str = "OPAQUE",
    priority: int = 0,
    recurrence: Optional[List[str]] = None,
    reminders: Optional[List[Dict]] = None,
    video_meeting_url: Optional[str] = None,
    send_notification: bool = True
) -> Any:
    """
    Create a new calendar event in default calendar
    기본 캘린더 일정 생성
    https://developers.worksmobile.com/kr/docs/calendar-default-event-user-create

    Args:
        summary: 일정의 내용 (필수)
        start_datetime: 시작 시간 (형식: YYYY-MM-DDTHH:mm:ss)
        end_datetime: 종료 시간 (형식: YYYY-MM-DDTHH:mm:ss)
        timezone: 타임존 (기본값: Asia/Seoul)
        description: 일정의 메모
        location: 일정의 장소
        event_id: 일정의 고유 ID (지정하지 않으면 자동 할당)
        category_id: 일정 카테고리 ID
        attendees: 참가자 정보 리스트
        visibility: 공개/비공개 (PUBLIC/PRIVATE, 기본값: PUBLIC)
        transparency: 바쁨/한가함 상태 (OPAQUE/TRANSPARENT, 기본값: OPAQUE)
        priority: 중요도 (0-9, 기본값: 0)
        recurrence: 반복 정보 리스트
        reminders: 알림 정보 리스트
        video_meeting_url: 화상회의 URL
        send_notification: 일정 알림 발송 여부 (기본값: true)

    Returns:
        dict: 생성된 이벤트의 세부 정보

    Example:
        await create_default_calendar_event(
            summary="팀 미팅",
            start_datetime="2024-01-15T14:00:00",
            end_datetime="2024-01-15T15:00:00",
            description="주간 팀 미팅",
            location="회의실 A",
            attendees=[
                {
                    "email": "user1@company.com",
                    "displayName": "김철수",
                    "partstat": "NEEDS-ACTION",
                    "isOptional": False
                }
            ]
        )
    """
    
    # 입력 검증
    if not summary or not summary.strip():
        raise ValueError("summary는 필수 입력값입니다.")
    
    try:
        # 시간 형식 검증
        datetime.fromisoformat(start_datetime)
        datetime.fromisoformat(end_datetime)
    except ValueError as e:
        raise ValueError(f"시간 형식이 올바르지 않습니다 (YYYY-MM-DDTHH:mm:ss): {e}")
    
    # 기본 이벤트 객체 생성
    event = {
        "summary": summary.strip(),
        "start": {
            "dateTime": start_datetime,
            "timeZone": timezone
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": timezone
        },
        "visibility": visibility,
        "transparency": transparency,
        "priority": priority
    }
    
    # 선택적 필드들 추가
    if event_id:
        event["eventId"] = event_id.strip()
    
    if description:
        event["description"] = description.strip()
    
    if location:
        event["location"] = location.strip()
    
    if category_id:
        event["categoryId"] = category_id.strip()
    
    if recurrence:
        event["recurrence"] = recurrence
    
    if attendees:
        # 참석자 정보 검증 및 설정
        validated_attendees = []
        for attendee in attendees:
            if not attendee.get("email") and not attendee.get("id"):
                continue  # 이메일이나 ID 중 하나는 필수
            
            validated_attendee = {
                "partstat": attendee.get("partstat", "NEEDS-ACTION"),
                "isOptional": attendee.get("isOptional", False),
                "isResource": attendee.get("isResource", False)
            }
            
            if attendee.get("email"):
                validated_attendee["email"] = attendee["email"]
            if attendee.get("id"):
                validated_attendee["id"] = attendee["id"]
            if attendee.get("displayName"):
                validated_attendee["displayName"] = attendee["displayName"]
            if attendee.get("resourceValue"):
                validated_attendee["resourceValue"] = attendee["resourceValue"]
                
            validated_attendees.append(validated_attendee)
        
        if validated_attendees:
            event["attendees"] = validated_attendees
    
    if video_meeting_url:
        event["videoMeeting"] = {
            "url": video_meeting_url
        }
    
    if reminders:
        # 알림 정보 검증
        validated_reminders = []
        for reminder in reminders:
            if reminder.get("method") not in ["DISPLAY", "EMAIL"]:
                continue
            
            validated_reminder = {
                "method": reminder["method"]
            }
            
            if reminder.get("trigger"):
                validated_reminder["trigger"] = reminder["trigger"]
            elif reminder.get("triggerDateTime"):
                validated_reminder["triggerDateTime"] = reminder["triggerDateTime"]
            
            validated_reminders.append(validated_reminder)
        
        if validated_reminders:
            event["reminders"] = validated_reminders
    
    # Request Body 구성
    request_body = {
        "eventComponents": [event],
        "sendNotification": send_notification
    }
    
    url = "https://www.worksapis.com/v1.0/users/me/calendar/events"
    post_headers = headers.copy()
    post_headers["Content-Type"] = "application/json"
    
    async with httpx.AsyncClient(headers=post_headers, timeout=30.0) as client:
        response = await client.post(url, json=request_body)
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "message": "일정이 성공적으로 생성되었습니다",
            "data": result,
            "status_code": response.status_code
        }
        


@mcp.tool()
async def delete_default_calendar_event(eventId: str) -> Any:
    """
    Delete a calendar event by its eventID
    기본 캘린더 일정 삭제
    https://developers.worksmobile.com/kr/docs/calendar-delete-event

    Args:
        eventId: The ID of the event to delete (required)

    Returns:
        dict: Result of the delete operation with status information
    """
    if not eventId:
        raise ValueError("eventId is required")

    url = f"https://www.worksapis.com/v1.0/users/me/calendar/events/{eventId}"
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.delete(url)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Event {eventId} deleted successfully",
            "status_code": response.status_code,
            "event_id": eventId
        }



############# Calendar #############

@mcp.tool()
async def get_calendar_personal_user_list(count: int = 50, cursor: str = "") -> Any:
    """
    Get the list of personal users in the calendar
    캘린더: 개인 속성 목록 조회
    https://developers.worksmobile.com/kr/docs/calendar-personal-user-list

    Args:
        count: Number of personal users to retrieve (min 1, max 50)
        cursor: Cursor for pagination, empty string for first page
    """
    url = f"https://www.worksapis.com/v1.0/users/me/calendar-personals"
    query_params = {
        "count": count,
        "cursor": cursor
    }
    
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()


@mcp.tool()
async def delete_calendar(calendarId: str) :
    """
    Delete a calendar by its ID
    캘린더 삭제
    https://developers.worksmobile.com/kr/docs/calendar-delete

    Args:
        calendarId: The ID of the calendar to delete (required)
        
    Returns:
        dict: Result of the delete operation with status information
        
    Raises:
        ValueError: If calendarId is empty or invalid
        HTTPError: If the API request fails
    """
    url = f"https://www.worksapis.com/v1.0/calendars/{calendarId}"
    
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.delete(url)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Calendar {calendarId} deleted successfully",
            "status_code": response.status_code,
            "calendar_id": calendarId
        }


@mcp.tool()
async def create_calendar(
    calendarName: str,
    description: str = "",
    members: list[dict] = None,
    isPublic: bool = False
) -> Any:
    """
    Create a new calendar
    캘린더 생성
    https://developers.worksmobile.com/kr/docs/calendar-create

Args:
        calendarName: Name of the calendar (required, maxLength: 50)
        description: Description of the calendar (optional, maxLength: 1000)
        members: List of calendar members (optional, unique items)
        isPublic: Whether the calendar is public (default: False)

    Returns:
        dict: Details of the created calendar
    """
    # Validate calendarName
    if not calendarName or len(calendarName) > 50:
        raise ValueError("calendarName is required and must be at most 50 characters long")

    # Validate description
    if len(description) > 1000:
        raise ValueError("description must be at most 1000 characters long")

    # Validate members
    if members is None:
        members = []
    else:
        for member in members:
            if "id" not in member or "type" not in member or "role" not in member:
                raise ValueError("Each member must have 'id', 'type', and 'role'")
            if member["type"] not in {"USER", "GROUP", "ORGUNIT"}:
                raise ValueError("member 'type' must be one of 'USER', 'GROUP', 'ORGUNIT'")
            if member["role"] not in {
                "CALENDAR_EVENT_READ_WRITE",
                "EVENT_READ_WRITE",
                "EVENT_READ",
                "EVENT_READ_FREE_BUSY",
            }:
                raise ValueError(
                    "member 'role' must be one of 'CALENDAR_EVENT_READ_WRITE', 'EVENT_READ_WRITE', 'EVENT_READ', 'EVENT_READ_FREE_BUSY'"
                )

    # API endpoint and headers
    url = "https://www.worksapis.com/v1.0/calendars"
    post_headers = headers.copy()
    post_headers["Content-Type"] = "application/json"
    
    # Request body
    request_body = {
        "calendarName": calendarName,
        "description": description,
        "members": members,
        "isPublic": isPublic,
    }

    # Make the API request
    async with httpx.AsyncClient(headers=post_headers) as client:
        response = await client.post(url, json=request_body)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    print('Starting works-mcp...')
     # stdio 방식으로 MCP 서버 실행
    mcp.run()