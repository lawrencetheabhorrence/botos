from abc import (
    ABC, abstractmethod
)
from distutils.dir_util import copy_tree
import json
import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Candidate, CandidateParty, CandidatePosition, Vote
)
from core.utils import AppSettings


# Test views.
class BaseElectionSettingsViewTest(ABC, TestCase):
    """
    This is the base class for the rest of the election settings view tests.
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Section')
        cls._admin_batch = Batch.objects.create(year=0)
        cls._admin_section = Section.objects.create(section_name='Superusers')

        User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='root',
            batch=cls._admin_batch,
            section=cls._admin_section,
            is_superuser=True
        )

        cls._view_url = ''

    def test_view_denies_anonymous_users(self):
        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

    def test_view_denies_non_superusers(self):
        User.objects.create_user(
            username='juan',
            email='juan@juan.com',
            password='123',
            batch=self._batch,
            section=self._section
        )

        self.client.login(username='juan', password='123')

        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(
            response,
            '/admin/login/?next=%2Fadmin%2Felection'
        )

    @abstractmethod
    def test_view_accepts_superusers(self):
        pass


class ElectionSettingsViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings view in the admin.

    The election settings view can be accessed via `/admin/election/`.
    Anonymous and non-superuser users will be redirected to the admin index
    page.

    This view allows modifying the following settings:
        - Current Template
        - Open/Close State of the Elections
            - Note: When the elections are open, the results will give each
                    candidate names and have their avatars changed to the
                    default one, but with some colour changes. On the flip
                    side, when the elections are closed, the results will
                    show the candidates' actual names and avatars.
        - Creation/Modification of Public/Private Keys For Vote Encryption
            - Note: This setting will be disabled if there are vote set
                    already, or the elections are open.

    TODO: - Add a button for this view that will purge votes, essentially
            resetting the elections. However, candidates, parties, and
            positions will remain intact.
          - Create a TODO.md file where the TODO items will be found in.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls._view_url = '/admin/election'

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')

        response = self.client.get(
            reverse('admin-election-index'),
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'default/admin/election.html'  # Default template is expected
                                           # since we did not set the template
                                           # in this test.
        )


# MBUI (Might Be Useful Info):
# (Jul. 23, 2019)
#     The classes below used to implement setUp(). The setUp() code logs in
#     an admin account in the test client. However, this is a bad idea since
#     the client will also log in with an admin account in tests that should
#     not have an admin logged in, including the tests in the base test class.


class ElectionSettingsCurrentTemplateViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings current template view.

    This view changes the current template being used. This will only accept
    POST requests. GET requests from superusers will result in a redirection
    to `/admin/election`, while non-superusers and anonymoous users to `/`.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._view_url = reverse('admin-election-template')

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_properly_redirects_get_requests(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('template', 'default')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Template field must not be empty nor have invalid data.'
        )
        self.assertEquals(AppSettings().get('template'), 'default')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('template', 'default')

        # We have to create an actual my-little-pony template since I still do
        # not know how to mock a template in Django. Let's just copy the
        # default template and rename the copied folder as 'yes-or-yes'. This
        # will remove the need to create a unique template and make this test
        # simpler. We may do this since this test is just going to test whether
        # or not the correct template is being rendered by Botos. This test
        # does not require the creation of a *unique* template. Future
        # revisions of Botos may choose to redo this in favour of mocking
        # instead.
        template_dir = os.path.join(settings.BASE_DIR, 'botos/templates')
        default_template_dir = os.path.join(template_dir, 'default')
        new_template_dir = os.path.join(template_dir, 'my-little-pony')
        copy_tree(default_template_dir, new_template_dir)

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(
            self._view_url,
            { 'template_name': 'my-little-pony' },
            follow=True
        )
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Current template changed successfully.'
        )
        self.assertEquals(AppSettings().get('template'), 'my-little-pony')

        # And, of course, we better clean up the mess we did and delete the
        # 'yes-or-yes' template we created.
        shutil.rmtree(new_template_dir)


class ElectionSettingsElectionsStateViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings election state view.

    This view changes the election state being used. An election state can
    either be open or closed. When the state is open, voters will be allowed to
    vote, and realtime results will show candidates with random names. This
    will only accept POST requests. GET requests from superusers will result in
    a redirection to `/admin/election`, while non-superusers and anonymoous
    users to `/`.

    This view must only accept a value that is either a True or False.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._view_url = reverse('admin-election-state')

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_properly_redirects_get_requests(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('election_state', 'open')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'You attempted to change the election state with invalid data.'
        )
        self.assertEquals(AppSettings().get('election_state'), 'open')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('election_state', 'open')

        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(
            self._view_url,
            { 'state': 'closed' },
            follow=True
        )
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Election state changed successfully.'
        )
        self.assertEquals(AppSettings().get('election_state'), 'closed')


class ElectionSettingsPubPrivKeysViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings public/private election keys view.

    This view changes the election state being used. An election state can
    either be open or closed. When the state is open, voters will be allowed to
    vote, and realtime results will show candidates with random names. This
    will only accept POST requests. GET requests from superusers will result in
    a redirection to `/admin/election`, while non-superusers and anonymoous
    users to `/`.

    Calling this view will immediately invoke Botos to generate a new set of
    public and private election keys. The keys will be used to encrypt and
    decrypt votes. However, if there are votes already or the elections are
    open, then calling this view will just simply send back a message that the
    operation cannot be performed due to the aformentioned conditions.
    """    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._view_url = reverse('admin-election-keys')

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_properly_redirects_get_requests(self):
        self.client.login(username='admin', password='root')
        response = self.client.get(self._view_url)
        self.assertRedirects(response, reverse('admin-election-index'))

    def test_view_messages_from_post_request(self):
        # Must return a success message to the view we'll be redirected to.
        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'New public and private election keys generated successfully.'
        )

    def test_view_disregards_params_in_post_requests(self):
        # View should still perform its task even if there are parameters in
        # the post request.
        self.client.login(username='admin', password='root')
        self.client.post(self._view_url, { 'this is a': 'param' })
        self.assertIsNotNone(AppSettings().get('public_election_key'))
        self.assertIsNotNone(AppSettings().get('private_election_key'))

    def test_view_with_empty_params_in_post_requests(self):
        self.client.login(username='admin', password='root')
        self.client.post(self._view_url, {})
        self.assertIsNotNone(AppSettings().get('public_election_key'))
        self.assertIsNotNone(AppSettings().get('private_election_key'))

    def test_view_but_with_votes_present(self):
        # Create the test non-superuser.
        _batch = Batch.objects.create(year=2020)
        _section = Section.objects.create(section_name='Emerald')
        _user = User.objects.create(
            username='juan',
            batch=_batch,
            section=_section
        )
        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        _candidate = Candidate.objects.create(
            user=_user,
            party=_party,
            position=_position
        )

        # Create a dummy vote.
        _vote = Vote.objects.create(
            user=_user,
            candidate=_candidate,
            vote_cipher=json.dumps(dict())
        )

        # public_election_key`and`private_election_key`must not change,
        # since votes are already present.
        AppSettings().set('public_election_key', 'am a barbie girl')
        AppSettings().set('private_election_key', 'in a barbie world')

        self.client.login(username='admin', password='root')
        response = self.client.post(self._view_url, {}, follow=True)
        response_messages = list(response.context['messages'])

        self.assertEquals(
            str(response_messages[0]),
            'Cannot generate public and private election keys since'
            + ' elections are open or votes have already been cast.'
        )

        self.assertEquals(
            AppSettings().get('public_election_key'),
            'am a barbie girl'
        )
        self.assertEquals(
            AppSettings().get('private_election_key'),
            'in a barbie world'
        )

    def test_view_but_with_votes_not_present(self):
        # public_election_key`and private_election_key`must change,
        # since votes are not present.
        AppSettings().set('public_election_key', 'all we hear is')
        AppSettings().set('private_election_key', 'radio gaga')

        self.client.login(username='admin', password='root')
        self.client.post(self._view_url, {})

        self.assertNotEquals(
            AppSettings().get('public_election_key'),
            'all we hear is'
        )
        self.assertNotEquals(
            AppSettings().get('private_election_key'),
            'radio gaga'
        )

    def test_view_but_with_elections_open(self):
        # public_election_key`and`private_election_key`must not change,
        # since the elections are open.
        AppSettings().set('election_state', 'open')
        AppSettings().set('public_election_key', 'break break break')
        AppSettings().set('private_election_key', 'breakthrough')

        self.client.login(username='admin', password='root')
        self.client.post(self._view_url, {})

        self.assertEquals(
            AppSettings().get('public_election_key'),
            'break break break'
        )
        self.assertEquals(
            AppSettings().get('private_election_key'),
            'breakthrough'
        )

    def test_view_but_with_elections_closed(self):
        # public_election_key`and`private_election_key`must change,
        # since the elections are closed.
        AppSettings().set('election_state', 'closed')
        AppSettings().set('public_election_key', 'years from now, i be like')
        AppSettings().set('private_election_key', 'wtf was i thinking')

        self.client.login(username='admin', password='root')
        self.client.post(self._view_url, {})

        self.assertNotEquals(
            AppSettings().get('public_election_key'),
            'years from now, i be like'
        )
        self.assertNotEquals(
            AppSettings().get('private_election_key'),
            'wtf was i thinking'
        )
