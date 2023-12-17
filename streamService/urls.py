"""streamService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, re_path
from mainApp import views


urlpatterns = [
    path("", views.index),
    path("login", views.checkPassAndLogin, name="login"),
    path("logout", views.logout),
    path("lk", views.lk),
    path("changePass", views.changePass),
    path("addAlbum", views.addAlbum),
    path("addAuthor", views.addAuthor),
    path("register", views.register),
    re_path(r"^admin/users$", views.adminUsers, name="adminUsers"),
    re_path(r"^admin/delUser$", views.delUser, name="delUsers"),
    re_path(r"static/libs/jquery/jquery.min.js$", views.register),
    re_path(r"static/libs/jquery/jquery-ui.css$", views.register),
    re_path(r"static/libs/jquery/jquery-ui.min.js$", views.register),
    re_path(r"static/libs/sha256.js$", views.register),
    re_path(r"^search$", views.search, name="search"),
    re_path(r"^autocompleteAuthor$", views.autocompleteAuthor, name="autocompleteAuthor"),
    re_path(r"^check$", views.checkPassAndLogin, name="checkPassAndLogin"),
    re_path(r"^deleteAlbum$", views.deleteAlbum, name="deleteAlbum"),
    re_path(r"^editAlbum$", views.editAlbum, name="editAlbum"),
    re_path(r"^album$", views.viewAlbum, name="viewAlbum"),
    re_path(r"^author$", views.viewAuthor, name="viewAuthor"),
    re_path(r"^editAuthor$", views.editAuthor, name="editAuthor"),
    re_path(r"^likeOrDislikeTrack$", views.likeOrDislikeTrack, name="likeOrDislikeTrack"),
    re_path(r"^checkAlbum$", views.checkAlbum, name="checkAlbum"),
]
