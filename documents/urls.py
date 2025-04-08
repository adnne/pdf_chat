from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, ConversationViewSet

router = DefaultRouter()
router.register('documents', DocumentViewSet, basename='document')
router.register('conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
]