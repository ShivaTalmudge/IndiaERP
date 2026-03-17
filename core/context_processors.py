def sidebar_context(request):
    ctx = {'user_role': None, 'user_company': None, 'user_profile': None}
    if request.user.is_authenticated:
        try:
            p = request.user.profile
            ctx['user_role'] = p.role
            ctx['user_company'] = p.company
            ctx['user_profile'] = p
        except Exception:
            pass
    return ctx
