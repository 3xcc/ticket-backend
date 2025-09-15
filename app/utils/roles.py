ROLE_PERMISSIONS = {
    "admin": ["view_ticket", "scan_ticket", "create_user", "edit_ticket", "delete_ticket", "export", "verify_payment", "delete_user", "create_event"],
    "subadmin": ["scan_ticket", "edit_ticket", "delete_ticket", "export"],
    "editor": ["scan_ticket", "edit_ticket"],
    "scanner": ["scan_ticket"]
}

def has_permission(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, [])
