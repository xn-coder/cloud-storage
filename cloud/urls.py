"""
URL configuration for cloud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from authentication.views import login, logout
from gallery.views import home, upload, media, get_media, fetch_video, stream_video, download_media
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('admin/', admin.site.urls),
    path('login/', login, name="login"),
    path("logout/", logout, name="logout"),
    path('get_media/', get_media, name="get_media"),
    path('fetch_video/', fetch_video, name="fetch_video"),
    path('stream_video/<str:video_id>/', stream_video, name='stream_video'),
    path('download_media/', download_media, name='download_media'),
    path('media/', media, name="media"),
    path("upload/", upload, name="upload"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)