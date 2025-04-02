from django import forms
from .models import Notification
from user.models import User,Employee


class NotificationForm(forms.ModelForm):
    
    def __init__(self, c_id, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['sender'].queryset = User.objects.filter(id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=c_id) )
        self.fields['recepients'].queryset = User.objects.filter(id__in = Employee.objects.values_list('user_id',flat=True).filter(company_id=c_id) )

    class Meta:

        model = Notification
        fields = ['sender','message']
    
    #recepients =  forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    recepients =  forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.SelectMultiple)

