from django.urls import path

from . import views
urlpatterns=[
    #path('',views.gallerylist, name='gallery')
    #path('',views.index, name='index'),
    path('login.html',views.login_view),
    path('base/gallery.html',views.gallerylist, name="gallery"),
    path('register/',views.register, name="register"),
    path('', views.login_view, name="login"),
    path('add/', views.uploadFile, name="add"),
    path ('logout',views.logout_view, name="logoutpage"),
    path('base/viewdetails.html',views.viewDetails, name="viewdetails"),
    path('base/delete.html',views.delete_object, name="delete"),
    path('base/edit.html',views.edit_object, name="edit"),
]