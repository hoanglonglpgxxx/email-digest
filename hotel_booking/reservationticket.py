class ReservationTicket:
    def __init__(self, customer_name, hotel_obj):
        self.customer_name = customer_name
        self.hotel_obj = hotel_obj

    def generate(self):
        content = f"""
        Thanks
        
        Your booking data:
        Name: {self.customer_name}
        Hotel name: {self.hotel_obj.name}
        """
        return content
