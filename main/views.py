from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from momonitor.main.models import (RESOURCE_NAME_MAP,
                                   Service,
                                   CodeServiceCheck,
                                   SensuServiceCheck,
                                   RESOURCES)

from momonitor.main.decorators import ajax_required
from django.contrib.auth.decorators import login_required
from momonitor.main.forms import RESOURCE_FORM_MAP

from momonitor.main.constants import (STATUS_GOOD,
                                      STATUS_BAD,
                                      STATUS_WARNING,
                                      STATUS_UNKNOWN)


'''Index page. Dashboard with services'''
@login_required
def index(request):
    request.breadcrumbs("Services",reverse("main:index"))

    services = Service.objects.all().order_by("id")
    return render_to_response("main/index.html",
                              {'services':services},
                              RequestContext(request))

'''Service Page. Shows checks per service'''
@login_required
def service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)

    request.breadcrumbs("Services",reverse("main:index"))
    request.breadcrumbs(service.name,reverse("main:service",kwargs={'service_id':service.id}))

    return render_to_response("main/service.html",
                              {'service':service},
                              RequestContext(request))

'''Modal Form that posts to Tastypie endpoints'''
@ajax_required
@login_required
def modal_form(request,resource_name,resource_id=None):
    if not RESOURCE_NAME_MAP.has_key(resource_name):
        raise Http404
    resource_cls = RESOURCE_NAME_MAP[resource_name]
    resource_form_cls = RESOURCE_FORM_MAP[resource_cls]

    if resource_id:
        instance = get_object_or_404(resource_cls,pk=resource_id)
        method="PUT"
        action = "/api/v1/%s/%s/?format=json" % (resource_cls.resource_name,
                                                 instance.id)
    else:
        instance = None
        method="POST"
        action="/api/v1/%s/?format=json" % (resource_cls.resource_name)

    #Most of this junk is to make tastypie happy. I regret using it. 
    if resource_cls == CodeServiceCheck:
        method="POST"

    if hasattr(instance,"service") or request.GET.has_key("sid"):
        form = resource_form_cls(instance=instance,
                                 initial={'service':instance.service.id if instance else request.GET.get("sid")})
    else:
        form = resource_form_cls(instance=instance)

    return render_to_response("%s%s" % ("main/",form.template),
                              {"form":form,
                               "action":action,
                               'method':method},
                              RequestContext(request))

'''Run a specific check.'''
@ajax_required
@login_required
def refresh(request,resource_name,resource_id):
    if not RESOURCE_NAME_MAP.has_key(resource_name):
        raise Http404
    resource_cls = RESOURCE_NAME_MAP[resource_name]
    resource = get_object_or_404(resource_cls,pk=resource_id)
    resource.update_status()
    return HttpResponse("OK")

'''Throw alert manually'''
@ajax_required
@login_required
def test_alert(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    service.send_alert(description="Test alert")
    return HttpResponse("OK")

'''We need a separate upload handler for code checks
 because tastypie is bad with uploading files'''
@login_required
def code_check_upload(request,instance_id=None):
    instance = None
    if instance_id:
        instance = get_object_or_404(CodeServiceCheck,pk=instance_id)

    if request.method == "DELETE":
        instance.delete()
        return HttpResponse("OK")

    form_cls = RESOURCE_FORM_MAP[CodeServiceCheck]
    form = form_cls(request.POST,request.FILES,instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse("main:service",kwargs={'service_id':request.POST.get('service')}))
    else:
        return HttpResponseBadRequest(form.errors.items())

'''Basic how it works page'''
@login_required
def how_it_works(request):
    request.breadcrumbs("Services",reverse("main:index"))
    request.breadcrumbs("How it works",reverse("main:how_it_works"))
    return render_to_response("main/how-it-works.html",{},RequestContext(request))

@ajax_required
@login_required
def sensu_check_info(request,sensu_check_id=None):
    check = get_object_or_404(SensuServiceCheck,pk=sensu_check_id)
    result_data = check.get_result_data()

    status_data = []
    for result in result_data:
        if result['status']==0:
            status=STATUS_GOOD
        elif result['status']==2:
            status=STATUS_BAD
        else:
            status=STATUS_UNKNOWN

        status_data.append({'client':result['client'],
                            'output':result['output'],
                            'status':status})

    return render_to_response("main/sensu-info-modal.html",
                              {'status_data':status_data,
                               'check':check},
                              RequestContext(request))
                               
    
@ajax_required
@login_required
def silence(request,resource_name,resource_id):
    if not RESOURCE_NAME_MAP.has_key(resource_name):
        raise Http404
    resource_cls = RESOURCE_NAME_MAP[resource_name]
    resource = get_object_or_404(resource_cls,pk=resource_id)
    resource.silenced = not resource.silenced
    resource.save()
    return HttpResponse("OK")
