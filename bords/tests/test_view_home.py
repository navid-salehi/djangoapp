from django.urls import reverse ,resolve
from django.test import TestCase
from ..views import BoardListView, board_topics, new_topic
from ..models import Bords, Topic, Post, User
from ..forms import NewTopicForm

class HomeTests(TestCase):
    def setUp(self):
        self.bords = Bords.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/form/')
        self.assertEquals(view.func.view_class, BoardListView)

    #def test_home_view_contains_link_to_topics_page(self):
    #    board_topics_url = reverse('board_topics', kwargs={'pk': self.bord.pk})
    #    self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

