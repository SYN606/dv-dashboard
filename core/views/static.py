from django.shortcuts import render


def terms_n_conditions(request):
    data = {"title": "Terms and condition for the bot."}
    return render(request, "TnC.html", data)


def privay_policy(request):
    data = {"title": "Privacy Policy page"}
    return render(request, "pp.html", data)
