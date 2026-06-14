JAZZMIN_SETTINGS = {
    "site_title": "DV Dashboard Core",
    "site_header": "DV Admin Console",
    "site_brand": "DV CLUSTER",
    "site_logo": "https://images.pexels.com/photos/29871288/pexels-photo-29871288.jpeg",
    "welcome_sign": "Welcome To Digital Vigital Control Panel",
    "copyright": "DV Dashboard Matrix",
    "search_model": ["core.GuildConfig"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Main Site", "url": "core:homepage"},
    ],
    "usermenu_links": [
        {"model": "core.guildconfig"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "core.GuildConfig": "fas fa-server",
        "core.AFK": "fas fa-clock",
        "core.AdminRole": "fas fa-user-shield",
        "core.MediaOnlyChannel": "fas fa-images",
        "core.StickyMessage": "fas fa-thumbtack",
        "core.DisabledCommand": "fas fa-ban",
        "core.RestrictedCommand": "fas fa-sliders-h",
        "core.TempbanConfig": "fas fa-cogs",
        "core.TempbanRecord": "fas fa-gavel",
        "core.ModerationLogConfig": "fas fa-clipboard-list",
        "core.ChannelPermissionSnapshot": "fas fa-camera",
        "core.VerificationConfig": "fas fa-shield-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "brand_colour": "navbar-dark bg-slate-900",
    "navbar": "navbar-dark bg-dark",
    "no_navbar_border": True,
    "sidebar": "sidebar-dark-primary",
    "actions_sidebar": False,
    "use_google_fonts": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}