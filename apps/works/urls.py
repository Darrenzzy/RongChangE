from rest_framework.routers import SimpleRouter

from works.views import CaseViewSet, DiseaseView, MedCaseView

router = SimpleRouter()

# 病例收集
# 我的病例 
router.register('case', CaseViewSet, basename='case')

# 新病例收集
router.register('med-case', MedCaseView, basename='med-case')

# 疾病模块
router.register('disease', DiseaseView, basename='disease')

urlpatterns = router.urls
