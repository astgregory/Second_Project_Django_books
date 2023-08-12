from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F, Prefetch
from django_filters.compat import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    # def setUp(self):
    #     self.user = User.objects.create(username='test_username')

    # def tearDown(self):
    #     # Удаление созданного пользователя из базы данных
    #     self.user.delete()

    def test_ok(self):
        user1 = User.objects.create(username='user1', first_name='Ivan', last_name='Petrov')
        user2 = User.objects.create(username='user2', first_name='Ivan', last_name='Sidorov')
        user3 = User.objects.create(username='user3', first_name='1', last_name='2')
        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name='Author 1', discount=20, owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Author 2', discount=35)
        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        rating=Avg('userbookrelation__rate'),
        coast_discount=F('price') - (F('price') * F('discount') / 100)
        ).prefetch_related(Prefetch('readers',
                                queryset=User.objects.all().only('first_name',
                                                                 'last_name'))).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'annotated_likes': 3,
                'rating': '4.67',
                'coast_discount': '20.00',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'annotated_likes': 2,
                'rating': '3.50',
                'coast_discount': '35.75',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    }
                ]
            },
        ]
        print(data)
        self.assertEqual(expected_data, data)
