from django import forms


from .models import Listing, Category, Bid, Comment


class NewTitle(forms.Form):
     title = forms.CharField(label="Enter Title")
     category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
     picture = forms.CharField(widget=forms.URLInput())
     description = forms.CharField(widget=forms.Textarea())
     price = forms.DecimalField()
   