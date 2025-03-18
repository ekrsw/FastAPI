from sqladmin import ModelView

from app.models.group import Group

class GroupAdminView(ModelView, model=Group):
    name_plural = "グループ"
    column_list = [
        Group.id,
        Group.groupname,
        Group.created_at,
        Group.updated_at
    ]
    column_searchable_list = [Group.groupname]
    column_sortable_list = [Group.id, Group.groupname]

    form_columns = [Group.groupname]