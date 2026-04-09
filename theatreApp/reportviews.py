from django.shortcuts import render,redirect
from .models import Show,Theatre
from MoviesApp.models import Booking
from django.db.models import Prefetch
from .views import theatre_login_required
from datetime import timedelta,date

# select theatre for report
@theatre_login_required
def Select_Theatre_For_Report(request):
    admin_id = request.session.get('theatreApp_id')

    if not admin_id:
        return redirect('taccount')
    else:
        t_obj = Theatre.objects.filter(user_id = admin_id)
        return render(request,'select_theatre_for_report.html',{'t_obj' : t_obj})



# sales report for particular theatre 
def theatre_sales_report(request,id):
    selected_movie = None
    if request.method == 'POST':
        selected_movie = request.POST.get('movie')

    shows = Show.objects.filter(theatre_id=id).prefetch_related(
            Prefetch('booking_set', queryset=Booking.objects.filter(status="confirmed"))
        )
    
    report = []
    movies = set()
    overall_total_tickets = 0
    overall_total_amount = 0 

    movies = set(show.movie.Title for show in shows)
    
    if selected_movie and selected_movie != "ALL":
        shows = shows.filter(movie__Title=selected_movie)




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

            "movie": show.movie.Title,
            "time": show.show_s_time,
            "tickets_sold": total_tickets,
            "total_revenue": total_amount,
        })
        overall_total_amount += total_amount
        overall_total_tickets += total_tickets 
    return render(request,'theatre_report.html',{'report':report,'overall_total_amount':overall_total_amount,'overall_total_tickets':overall_total_tickets,'movies': list(movies),'selected_movie':selected_movie})

def select_show(request):
    shows = Show.objects.all()
    return render(request,'select_show.html',{"shows":shows})

def booking_details(request,id):
    show = Show.objects.get(id=id)

    start = show.show_s_date
    end = show.show_e_date
    date_list = []

    current = start
    while current <= end:
        date_list.append(current)
        current += timedelta(days=1)

    input_date = request.POST.get('date')
    print(input_date)

    if input_date:
        input_date = date.fromisoformat(input_date)
    else:
        input_date = start

    bookings = Booking.objects.filter(show_id=id,date=input_date)
    print(bookings)
    return render(request,'show_bookings.html',{'bookings':bookings,"dates":date_list,'selected_date': input_date})