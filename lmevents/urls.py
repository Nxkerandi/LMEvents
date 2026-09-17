from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# django.conf.urls.static.static() no-ops when DEBUG=False (by design, for real
# deployments fronted by a CDN/object storage). This app has no such setup yet,
# so media is served directly by Django regardless of DEBUG — fine at this scale.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_static, {'document_root': settings.MEDIA_ROOT}),
]

# Mounted at root (not /events/) so registration links read as
# <domain>/<slug>/ instead of .../events/<slug>/. Must stay last — events.urls'
# <slug:slug>/ pattern would otherwise swallow "admin" or "media" as an event slug.
urlpatterns += [
    path('', include('events.urls')),
]
