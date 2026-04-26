from rest_framework.routers import DefaultRouter
from .views import FieldUpdateViewSet

router = DefaultRouter()
router.register("", FieldUpdateViewSet, basename="updates")
urlpatterns = router.urls
