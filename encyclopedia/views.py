from django.shortcuts import render
from django import forms
from markdown2 import Markdown
import random
from . import util

class NewEntryForm(forms.Form):
    entry_title = forms.CharField(label="Title")
    entry_content = forms.CharField(label="Content", widget=forms.Textarea(attrs={
        'rows': 6, 
        'cols': 35,
        'style': 'width: 400px; height: 150px;'
    }))


class EditEntryForm(forms.Form):
    entry_content = forms.CharField(label="Content", widget=forms.Textarea(attrs={
        'rows': 10, 
        'cols': 50,
        'style': 'width: 500px; height: 300px;'
    }))


markdowner = Markdown()


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# Function that displays an entry
def wiki(request, title):
    content = util.get_entry(title)
    
    # Check if the entry exists
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"Requested page '{title}' was not found."
        })
    
    html_converted = markdowner.convert(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_converted,
    })


# Function that handles search function
def search(request):
    # Get the text from the search field
    query = request.GET.get('q', '')
    
    if not query:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    
    # If query doesn't match entry title
    if util.get_entry(query) is None:
        # Check for partial matches
        all_entries = util.list_entries()
        partial_matches = [entry for entry in all_entries if query.lower() in entry.lower()]
        
        if partial_matches:
            # Return list of partial matches
            return render(request, "encyclopedia/search_results.html", {
                "query": query,
                "matches": partial_matches
            })
        else:
            # No matches found
            return render(request, "encyclopedia/error.html", {
                "message": f"No entries found matching '{query}'."
            })

    # Yes, query matches entry title
    return wiki(request, query)


# Function that handles new entries
def new(request):
    # Check if request method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = NewEntryForm(request.POST)
        
        # Check if form data is valid
        if form.is_valid():
            # Isolate the title and content from the cleaned data
            title = form.cleaned_data["entry_title"]
            content = form.cleaned_data["entry_content"]
            
            # Check if entry already exists
            if util.get_entry(title) is not None:
                return render(request, "encyclopedia/new.html", {
                    "form": form,
                    "error": "Entry already exists with that title. Try again."
                })
            
            # Add the title as H1 at the top of the content
            content_with_title = f"# {title}\n\n{content}"
            
            # Save the new entry
            util.save_entry(title, content_with_title)
            
            # Redirect to the new entry
            return wiki(request, title)
    else:
        # Create a new form
        form = NewEntryForm()
    
    return render(request, "encyclopedia/new.html", {
        "form": form
    })


# Function that handles editing an entry
def edit(request, title):
    # Check if the entry exists
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"Requested page '{title}' was not found."
        })
    
    # Check if the request is POST (user saves)
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = EditEntryForm(request.POST)

        # Check if form data is valid
        if form.is_valid():
            # Isolate the content from the cleaned data
            content = form.cleaned_data["entry_content"]

            # Save the modified entry
            util.save_entry(title, content)
            
            # Redirect to the edited entry
            return wiki(request, title)
    else:
        # Pre-populate the form with existing content
        form = EditEntryForm(initial={"entry_content": content})

    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title
    })


# Function that handles loading a random page
def random_page(request):
    # Get all entries and select a random one
    entries = util.list_entries()
    title = random.choice(entries)
    return wiki(request, title)