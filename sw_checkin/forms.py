from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField()
    email.widget.attrs['class'] = 'form-control'


class NameForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    first_name.widget.attrs['class'] = 'form-control'
    first_name.label = 'First Name'

    last_name = forms.CharField(max_length=30)
    last_name.widget.attrs['class'] = 'form-control'
    last_name.label = 'Last Name'


class ReservationForm(forms.Form):
    confirmation_num = forms.CharField(max_length=13)
    confirmation_num.widget.attrs['class'] = 'form-control'
    confirmation_num.label = 'Confirmation Code'

    flight_date = forms.DateField()
    flight_date.widget.attrs['class'] = 'form-control'
    flight_date.label = 'Date'

    flight_time = forms.TimeField()
    flight_time.help_text = "Time in PST in 24 hr time. Ex. 13:30."
    flight_time.widget.attrs['class'] = 'form-control'
    flight_time.label = 'Time'

