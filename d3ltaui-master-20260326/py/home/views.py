from django.shortcuts import render

def index(request):
    context = {"title": "Home"}
    return render(request, "home.html", context)


def help_page(request):
    context = {
        "title": "Help",
        "nav_selected_item": "help",
    }
    return render(request, "help.html", context)
