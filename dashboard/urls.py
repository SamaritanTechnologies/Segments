from django.urls import path

from .views import DashboardView, DeleteSegmentView, UpdateSegmentTraitsView, AnalyzeQuestion

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('update/<int:pk>/', UpdateSegmentTraitsView.as_view(), name="update_segment"),
    path('delete/<int:pk>/', DeleteSegmentView.as_view(), name="delete_segment"),
    path('analyze/', AnalyzeQuestion.as_view(), name="analyze_questions")
]