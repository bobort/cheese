from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class CrispyFormMixin(object):
    __form_helper = None  # type: FormHelper
    layout = None  # type: Layout

    @property
    def helper(self):
        if not self.__form_helper:
            form_helper = FormHelper()
            form_helper.form_tag = False
            form_helper.html5_required = True
            form_helper.layout = self.layout
            self.__form_helper = form_helper
        return self.__form_helper
