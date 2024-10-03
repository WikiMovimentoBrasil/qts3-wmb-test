from datetime import datetime

from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.models import Batch
from core.parsers.base import ParserException
from core.parsers.v1 import V1CommandParser
from core.parsers.csv import CSVCommandParser


@require_http_methods(
    [
        "GET",
    ]
)
def home(request):
    """
    Main page for this tool
    """
    return render(request, "index.html")


@require_http_methods(
    [
        "GET",
    ]
)
def batch(request, pk):
    """
    Base call for a batch. Returns the main page, that will load 2 fragments: commands and summary
    Used for ajax calls
    """
    try:
        batch = Batch.objects.get(pk=pk)
        return render(request, "batch.html", {"batch": batch})
    except Batch.DoesNotExist:
        return render(request, "batch_not_found.html", {"pk": pk}, status=404)


def new_batch(request):
    """
    Creates a new batch
    """
    if request.method == "POST":
        try:
            batch_owner = "anonymous"
            batch_commands = request.POST.get("commands")
            batch_name = request.POST.get("name", f"Batch  user:{batch_owner} {datetime.now().isoformat()}")
            batch_type = request.POST.get("type", "v1")
            request.session["preferred_batch_type"] = batch_type

            batch_commands = batch_commands.strip()
            if not batch_commands:
                raise ParserException("Command string cannot be empty")

            batch_name = batch_name.strip()
            if not batch_name:
                raise ParserException("Batch name cannot be empty")

            if batch_type == "v1":
                parser = V1CommandParser()
            else:
                parser = CSVCommandParser()
            
            batch = parser.parse(batch_name, batch_owner, batch_commands)
            return redirect(reverse("batch", args=[batch.pk]))
        except ParserException as p:
            error = p.message
        except Exception as p:
            error = str(p)
        return render(
            request,
            "new_batch.html",
            {
                "error": error,
                "name": batch_name,
                "batch_type": batch_type,
                "commands": batch_commands,
            },
        )

    else:
        preferred_batch_type = request.session.get("preferred_batch_type", "v1")
        return render(
            request,
            "new_batch.html",
            {
                "batch_type": preferred_batch_type,
            }
        )
