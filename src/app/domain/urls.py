INDEX = "/"
SITE_ROOT = "/{path:str}"
OPENAPI_SCHEMA = "/schema"

TAG_LIST = "/api/tags"
TAG_CREATE = "/api/tags"
TAG_UPDATE = "/api/tags/{tag_id:uuid}"
TAG_DELETE = "/api/tags/{tag_id:uuid}"
TAG_DETAILS = "/api/tags/{tag_id:uuid}"

ACCOUNT_LOGIN = "/api/access/login"
ACCOUNT_REGISTER = "/api/access/signup"
ACCOUNT_PROFILE = "/api/me"
ACCOUNT_LIST = "/api/users"
ACCOUNT_DELETE = "/api/users/{user_id:uuid}"
ACCOUNT_DETAIL = "/api/users/{user_id:uuid}"
ACCOUNT_UPDATE = "/api/users/{user_id:uuid}"
ACCOUNT_CREATE = "/api/users"

TEAM_LIST = "/api/teams"
TEAM_DELETE = "/api/teams/{team_id:uuid}"
TEAM_DETAIL = "/api/teams/{team_id:uuid}"
TEAM_UPDATE = "/api/teams/{team_id:uuid}"
TEAM_CREATE = "/api/teams"
TEAM_INDEX = "/api/teams/{team_id:uuid}"
TEAM_INVITATION_LIST = "/api/workspaces/{team_id:uuid}/invitations"


STATS_WEEKLY_NEW_USERS = "/api/stats/weekly-new-users"
