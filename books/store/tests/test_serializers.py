from unittest import TestCase

from django.contrib.auth.models import User

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username7')

    def tearDown(self):
        # Удаление созданных книг и пользователя из базы данных
        Book.objects.all().delete()
        self.user.delete()

    def test_ok(self):
        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name='Author 1', owner=self.user)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Author 2', owner=self.user)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'owner': book_1.owner.id
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'owner': book_2.owner.id
            }
        ]

        self.assertEqual(expected_data, data)