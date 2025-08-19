### 适配升级django4.2

* django 4.2 废弃方法
```text

from django.utils.translation import ugettext as _
from django.utils.translation import gettext as _


from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _


ugettext            ->      gettext
ugettext_lazy       ->      gettext_lazy

```
