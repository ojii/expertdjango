from django import template, http
from django.conf import settings
from django.dispatch.dispatcher import Signal
from django.template import loader
from django.template.loader import render_to_string, BaseLoader
from django.test.testcases import TestCase


build_response = Signal()

def buildresponse(sender, **kwargs):
    for name in dir(http):
        obj = getattr(http, name)
        if getattr(obj, 'status_code', None) == sender.status_code:
            sender.response = obj(sender.content)
            return
build_response.connect(buildresponse)

view = Signal()

class expertmiddleware:
    def __init__(self):
        loader.template_source_loaders = (templateloader(),)
    
    def process_request(self, request):
        view.send(sender=request)
        if hasattr(request, 'response'):
            return request.response

render_template = Signal()

def render(sender, **kwargs):
    sender.rendered_template = render_to_string(sender.template_name, sender.context)

render_template.connect(render)


class templateloader(BaseLoader):
    def load_template(self, template_name, template_dirs=None):
        if template_name in ['404.html', '500.html']:
            return template.Template(template_name[:3]), None
        else:
            for receiver in view.receivers:
                templates = getattr(receiver[1], 'templates', {})
                tpl = templates.get(template_name, None)
                if tpl:
                    return tpl, None
        return template.Template('Fallback'), None



class Tests(TestCase):
    def test_1(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, '404')
        
    def test_2(self):
        class MyView(object):
            templates = {
                '1.html': template.Template('Hello {{ name }}')
            }
            
            def __call__(self, sender, **kwargs):
                self.template_name = '1.html'
                self.context = {'name': 'Test'}
                render_template.send(sender=self)
                self.status_code = 200
                self.content = self.rendered_template
                build_response.send(sender=self)
                sender.response = self.response
                
        view.connect(MyView(), weak=False)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'Hello Test')
        
    def test_3(self):
        class MyView(object):
            def __call__(self, sender, **kwargs):
                self.template_name = '2.html'
                self.context = {'name': 'Test'}
                render_template.send(sender=self)
                self.status_code = 200
                self.content = self.rendered_template
                build_response.send(sender=self)
                sender.response = self.response
                
        view.connect(MyView(), weak=False)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'Fallback')
