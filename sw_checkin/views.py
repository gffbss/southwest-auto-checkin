from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from sw_checkin.forms import EmailForm, ReservationForm
from sw_checkin.models import Passenger, Reservation


def email_view(request):
    if request.method == 'POST':
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            form_email = email_form.cleaned_data['email']
            passenger, created = Passenger.objects.get_or_create(email=form_email)
            return HttpResponseRedirect(reverse('reservation', args=[passenger.id]))

    else:
        email_form = EmailForm()

    return render(request, 'email.html', {
        'email_form': email_form,
    })


def reservation_view(request, passenger_id):
    passenger = get_object_or_404(Passenger, id=passenger_id)

    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)
        if reservation_form.is_valid():
            passenger.first_name = reservation_form.cleaned_data['first_name']
            passenger.last_name = reservation_form.cleaned_data['last_name']
            passenger.save()
            confirmation_num = reservation_form.cleaned_data['confirmation_num']
            flight_date = reservation_form.cleaned_data['flight_date']
            flight_time = reservation_form.cleaned_data['flight_time']
            reservation = Reservation.objects.create(
                passenger=passenger,
                flight_date=flight_date,
                flight_time=flight_time,
                confirmation_num=confirmation_num
            )
            return HttpResponseRedirect(reverse('success', args=[reservation.id]))
    else:
        reservation_form = ReservationForm(
            initial={
                'first_name': passenger.first_name,
                'last_name': passenger.last_name,
            })

    return render(request, 'create-reservation.html', {
        'reservation_form': reservation_form,
        'passenger': passenger,
    })


def success_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'success.html', {
        'reservation': reservation
    })

