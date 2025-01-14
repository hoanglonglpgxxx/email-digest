import pandas

df = pandas.read_csv('hotels.csv')
class Hotel:
    def __init__(self, hotel_id):
        self.hotel_id = hotel_id
        self.name = df.loc[df['id'] == self.hotel_id, 'name'].squeeze()

    def book(self):
        """
        Book a hotel by changing its availability to NO
        :return:
        :rtype:
        """
        df.loc[df['id'] == self.hotel_id, 'available'] = 'no'
        df.to_csv('hotels.csv', index=False)

    def available(self):
        """
        Check if hotel is available
        :return: True or False
        :rtype: bool
        """
        availability = df.loc[df['id'] == self.hotel_id, 'available'].squeeze()
        if availability == 'yes':
            return True
        else:
            return False

# hotel2 = Hotel(134)
# print(hotel2.available())