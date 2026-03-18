def sidebar_context(request):
    """Provide common context for templates, leveraging middleware attributes."""
    if not request.user.is_authenticated:
        return {'user_role': None, 'user_company': None, 'user_profile': None}
    
    return {
        'user_role':    getattr(request, 'user_role', None),
        'user_company': getattr(request, 'company', None), 
        'user_profile': getattr(request, 'profile', None),
    }
