from user import User
from hotel import Hotel
from reservationticket import ReservationTicket

hotel_id = input('Enter the id of hotel: ')
hotel = Hotel(int(hotel_id))
if hotel.available():
    hotel.book()
    name = input('Enter ur name: ')
    reservation_ticket = ReservationTicket(customer_name = name, hotel_obj=hotel)
    print(reservation_ticket.generate())
else:
    print('Hotel is not available!')