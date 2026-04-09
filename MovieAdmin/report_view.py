from django.shortcuts import render,redirect
from .models import AddMovie
from theatreApp.models import Show,Theatre
from MoviesApp.models import Booking
from django.db.models import Prefetch
from .views import movie_login_required 
from datetime import timedelta,date
from django.db.models import Q



# choose movie
@movie_login_required
def Select_Movie_For_Report(request):
    admin_id = request.session.get('movieApp_id')
    m_obj = AddMovie.objects.filter(user_id = admin_id)
    movie = request.POST.get('movie')
    if movie:
        m_obj = AddMovie.objects.filter(Q(Title__icontains=movie) | Q(discription__icontains=movie) | Q(Category__icontains=movie)) if movie else []
    if request.POST.get('all'):
        m_obj = AddMovie.objects.filter(user_id = admin_id)
    return render(request,'select_movie_for_report.html',{'m_obj' : m_obj})



# movie sales report
def movie_sales_report(request,id):
    selected_theatre = None
    if request.method == 'POST':
        selected_theatre = request.POST.get('theatre')

    shows = Show.objects.filter(movie_id=id).prefetch_related(
            Prefetch('booking_set', queryset=Booking.objects.filter(status="confirmed"))
        )
    
    report = []
    theatres = set()
    overall_total_tickets = 0
    overall_total_amount = 0 

    theatres = set((show.theatre.id, show.theatre.name, show.theatre.location) for show in shows)
    
    if selected_theatre and selected_theatre != "ALL":
        shows = shows.filter(theatre__id=selected_theatre)

    for show in shows:
        
        total_tickets = 0
        total_amount = 0
        start_date = show.show_s_date
        end_date = show.show_e_date
        delta = (end_date - start_date).days

        for i in range(delta + 1):
            current_date = start_date + timedelta(days=i)
        
            bookings_on_date = [b for b in show.booking_set.all() if b.date == current_date]
            total_tickets = sum(len(b.seats) for b in bookings_on_date)
            total_amount = sum(float(b.amount) for b in bookings_on_date)

            report.append({
            "date": current_date,

            "theatre": show.theatre.name,
            "location":show.theatre.location,
            "time": show.show_s_time,
            "tickets_sold": total_tickets,
            "total_revenue": total_amount,
        })
        overall_total_amount += total_amount
        overall_total_tickets += total_tickets 
    
    return render(request,'movie_report.html',{'report':report,'overall_total_amount':overall_total_amount,'overall_total_tickets':overall_total_tickets,'theatres': list(theatres),'selected_theatre':selected_theatre})

