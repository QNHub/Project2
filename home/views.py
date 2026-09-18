from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'Job Website'
    return render(request, 'home/index.html', {
        'template_data': template_data})