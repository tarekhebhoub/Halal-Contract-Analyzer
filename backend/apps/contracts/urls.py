from rest_framework.routers import DefaultRouter
from .views import ContractViewSet

router = DefaultRouter()
router.register(r"contracts", ContractViewSet, basename="contract")

urlpatterns = router.urls
