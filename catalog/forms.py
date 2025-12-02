from django import forms
from .models import User, Order
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО', max_length=100)
    email = forms.EmailField(required=True)
    agreement = forms.BooleanField(required=True, label='Согласие на обработку персональных данных')

    class Meta:
        model = User
        fields = ("full_name", "username", "email", "password1", "password2", "agreement")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = self.cleaned_data["full_name"]
        user.agreement = self.cleaned_data["agreement"]
        if commit:
            user.save()
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } #dwa