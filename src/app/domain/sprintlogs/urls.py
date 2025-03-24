detail_route = "/detail/{row_id:uuid}"
project_route = "/project/{project_type:str}"
user_route = "/tasks/user/{user_id:uuid}"
active_project_route = "/projects/user/{user_id:uuid}"

SPRINTLOG_LIST = "/api/sprintlogs/{project_type:str}"
SPRINTLOG_DETAIL = "/api/sprintlogs/{row_id:uuid}"
SPRINTLOG_UPDATE = "/api/sprintlogs/{row_id:uuid}"
SPRINTLOG_DELETE = "/api/sprintlogs/{row_id:uuid}"
SPRINTLOG_CREATE = "/api/sprintlogs/create"

SPRINTLOG_DETAIL_BY_SLUG = "/api/sprintlogs/slug/{slug:str}"

SPRINTLOG_BACKLOG_TASK_BY_PROJECT = "/api/sprintlogs/project/{project_type:str}"
SPRINTLOG_PROJECT_BY_USER = "/api/sprintlogs/projects/user/{user_id:uuid}"

SPRINTLOG_TASK_BY_USER = "api/sprintlogs/tasks/user/{user_id:uuid}"


SPRINTLOG_PROGRESS_UP = "/api/sprintlogs/project/up/{slug:str}"
SPRINTLOG_PROGRESS_DOWN = "/api/sprintlogs/project/down/{slug:str}"
SPRINTLOG_PROGRESS_COMPLETE = "/api/sprintlogs/progress/complete/{slug:str}"

SPRINTLOG_PROGRESS_CIRCLE = "/api/sprintlogs/progress/circle/{slug:str}"
SPRINTLOG_PRIORITY_CIRCLE = "/api/sprintlogs/priority/circle/{slug:str}"
SPRINTLOG_STATUS_CIRCLE = "/api/sprintlogs/status/circle/{slug:str}"

SPRINTLOG_SWITCH_TASK = "/api/sprintlogs/switch/task/{slug:str}"
SPRINTLOG_SWITCH_BACKLOG = "/api/sprintlogs/switch/backlog/{slug:str}"
