PROJECT_LIST = "/api/projects"
PROJECT_DETAIL = "/api/projects/{id:uuid}"
PROJECT_UPDATE = "/api/projects/{id:uuid}"
PROJECT_STATUS_UPDATE = "/api/projects/status/{id:uuid}"

PROJECT_DELETE = "/api/projects/{id:uuid}"
PROJECT_CREATE = "/api/projects/create"
PROJECT_DETAIL_BY_SLUG = "/api/projects/slug/{slug:str}"

PROJECT_ADD_TEAM = f"/api/projects/teams/assign"
PROJECT_REMOVE_TEAM = f"/api/projects/teams/remove"
