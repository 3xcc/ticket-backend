ROLE_PERMISSIONS = {
    "admin": ["create_user", "edit_ticket", "delete_ticket", "export", "verify_payment"],
    "subadmin": ["edit_ticket", "delete_ticket", "export"],
    "editor": ["edit_ticket"],
    "scanner": ["scan_ticket"]
}

def has_permission(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, [])
