#-*- coding: utf-8 -*-
from django import forms
from borgia.validators import *
from notifications.models import NotificationTemplate
import re


class notiftest(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255,
                                widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                validators=[autocomplete_username_validator])

    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)


class NotificationTemplateUpdateViewForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ['message_template', 'category_template', 'type_template', 'is_activated']

    def clean_message_template(self):
        regex = re.compile(r"{{.*?}}")
        list = regex.findall(self.cleaned_data['message_template'])

        regex = re.compile(r"(?:{{ *| *}})")
        # Compiler l'expression regex avant une boucle permet d'améliorer les performances
        for e in enumerate(list):
            list[e[0]] = regex.sub("", e[1])
            
        authorized_tags = ("recipient",
                           "recipient.surname",
                           "recipient.first_name",
                           "recipient.last_name")

        for e in list:
            if e not in authorized_tags:
                raise ValidationError("Utilisation de tags non autorisés ou mal orthographiés")

        return self.cleaned_data['message_template']



