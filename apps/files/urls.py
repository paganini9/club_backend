from django.urls import path

from apps.files.views import FileDetailView, FileListView, FileUploadView

urlpatterns = [
    path("", FileListView.as_view(), name="file-list"),
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("<int:pk>/", FileDetailView.as_view(), name="file-detail"),
]
