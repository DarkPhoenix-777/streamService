from django import forms


class loginForm(forms.Form):
    login = forms.CharField(required=True, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')


class registerForm(forms.Form):
    login = forms.CharField(required=True, label='Логин')
    passHash = forms.CharField(widget=forms.PasswordInput, required=True, label='Пароль')
    username = forms.CharField(required=True, label='Имя пользователя')

