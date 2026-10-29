from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from .models import Book, BookInstance


class LoanedBooksAllListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='member', password='password')
        self.borrower = User.objects.create_user(
            username='borrower',
            password='password',
            first_name='Ada',
            last_name='Lovelace',
        )
        self.book = Book.objects.create(
            title='A borrowed book',
            summary='A book on loan.',
            isbn='1234567890123',
        )
        BookInstance.objects.create(
            book=self.book,
            imprint='Library',
            borrower=self.borrower,
            status='o',
        )
        available_book = Book.objects.create(
            title='An available book',
            summary='A book on the shelf.',
            isbn='1234567890124',
        )
        BookInstance.objects.create(
            book=available_book,
            imprint='Library',
            borrower=self.user,
            status='a',
        )
        content_type = ContentType.objects.get_for_model(BookInstance)
        self.permission = Permission.objects.get(
            content_type=content_type,
            codename='can_mark_returned',
        )

    def test_requires_authentication_and_librarian_permission(self):
        for route_name in ('all-borrowed', 'borrowed'):
            url = reverse(route_name)
            self.assertRedirects(
                self.client.get(url),
                f'{reverse("account_login")}?next={url}',
                fetch_redirect_response=False,
            )

        self.client.force_login(self.user)
        for route_name in ('all-borrowed', 'borrowed'):
            self.assertEqual(self.client.get(reverse(route_name)).status_code, 403)

    def test_librarian_sees_all_on_loan_books_and_borrower_names(self):
        self.user.user_permissions.add(self.permission)
        self.client.force_login(self.user)

        response = self.client.get(reverse('all-borrowed'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertContains(response, 'Ada Lovelace')
        self.assertNotContains(response, 'An available book')
        self.assertEqual(len(response.context['bookinstance_list']), 1)
