from rest_framework.routers import DefaultRouter
from .views import FieldViewSet

router = DefaultRouter()
router.register("", FieldViewSet, basename="fields")
urlpatterns = router.urls
