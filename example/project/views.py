from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.html import format_html



@login_required
def index(request):
    messages.info(request, format_html("""
You can populate the Sample table manually or using the management command <b>create_samples</b>.<br />
Then, run the management command <b>clean_tables</b> and see what happens ...</br>
<br />
Also, try different values for <b>TABLES_CLEANER_TABLES</b> in project's settings.
"""))
    return HttpResponseRedirect('/admin/')
