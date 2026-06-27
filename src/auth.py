"""
Simple role-based access control for the intake attrition dashboard.
"""

USER_CREDENTIALS = {
    'Intake Coordinator': 'coordinator123',
    'Counselor / Social Worker': 'counselor123',
    'Program Manager': 'manager123',
}

ROLE_PAGE_ACCESS = {
    'Intake Coordinator': [
        'Home / Overview',
        'Risk Dashboard',
        'Client Profile',
        'Analytics',
    ],
    'Counselor / Social Worker': [
        'Home / Overview',
        'Risk Dashboard',
        'Client Profile',
    ],
    'Program Manager': [
        'Home / Overview',
        'Analytics',
    ],
}

ROLE_DESCRIPTIONS = {
    'Intake Coordinator': 'Track new clients, follow up on appointments, and prioritize outreach.',
    'Counselor / Social Worker': 'Review risks, identify barriers, and support client interventions.',
    'Program Manager': 'Monitor trends, attrition rates, and process bottlenecks.',
}


def authenticate_user(role: str, password: str) -> bool:
    """Return True if the provided password is valid for the selected role."""
    return USER_CREDENTIALS.get(role) == password
