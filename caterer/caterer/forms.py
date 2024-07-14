from typing import Any
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from catrinmodel.models import caterer,Food,CatarerFood,Order,MenuCatagory

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(CreateUserForm,self).__init__(*args, **kwargs)
        last_id=User.objects.last()
        print(last_id.id)
        self.initial['username']='userid834'+str(last_id.id+1)


class CatererForm(forms.ModelForm):
    class Meta:
        model = caterer
        fields = '__all__'


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCatagory
        fields = '__all__'

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = '__all__'