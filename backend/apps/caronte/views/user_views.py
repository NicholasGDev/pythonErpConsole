# kept for backward compatibility — classes live in separate modules now
from apps.caronte.views.user_list_view import UserListView
from apps.caronte.views.user_detail_view import UserDetailView

__all__ = ['UserListView', 'UserDetailView']