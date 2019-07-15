import json

from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.test import TestCase

from core.models import (
    Vote, Candidate, CandidateParty, CandidatePosition, ElectionSetting,
    User, Batch, Section
)


class VoteTest(TestCase):
    """
    Tests the Vote model.

    The Vote model must have the following custom fields:
        - user (foreign key)
        - candidate (foreign key)
        - vote_cipher

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The user field must be a one-to-one field and have the following settings:
        - to = 'User'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - related_name = 'votes'

    The candidate field must be a foreign key and have the following settings:
        - to = 'Candidate'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'votes'

    The vote_cipher field must be a JSON field and have the following settings:
        - null = False
        - blank = False
        - default = None
        - unique = True (for privacy reasons; having the same resulting cipher
                         will weaken privacy since, once you are able to
                         figure out the original value of a cipher, you will
                         obviously automatically know the value of duplicate
                         ciphers.)

    The vote_cipher field will contain the encrypted vote of a user for a
    candidate. The Paillier homeomorphic cryptosystem is used to
    encrypt/decrypt votes.

    The model must have the following meta settings:
        - Index must be set to the user field and the candidate field.
        - The ordering must be based on the candidate position level first,
          then the candidate last name, and lastly, the candidate first name.
        - The singular verbose name will be "vote", with the plural being
          "votes".

    The __str__() method should return
    "<Vote for '{candidate username}' by '{ user username }'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Emerald')
        cls._user = User.objects.create(
            username='juan',
            batch=cls._batch,
            section=cls._section
        )
        cls._party = CandidateParty.objects.create(party_name='Awesome Party')
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate = Candidate.objects.create(
            user=cls._user,
            party=cls._party,
            position=cls._position
        )
        cls._vote = Vote.objects.create(
            user=cls._user,
            candidate=cls._candidate,
            vote_cipher=json.dumps(dict())
        )
        cls._vote_user_field = cls._vote._meta.get_field('user')
        cls._vote_candidate_field = cls._vote._meta.get_field('candidate')
        cls._vote_cipher_field = cls._vote._meta.get_field('vote_cipher')

    # Test user foreign key.
    def test_user_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._vote_user_field, models.ForeignKey)
        )

    def test_user_fk_connected_model(self):
        connected_model = getattr(
            self._vote_user_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, User)

    def test_user_fk_on_delete(self):
        on_delete_policy = getattr(
            self._vote_user_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_user_fk_null(self):
        self.assertFalse(self._vote_user_field.null)

    def test_user_fk_blank(self):
        self.assertFalse(self._vote_user_field.blank)

    def test_user_fk_default(self):
        self.assertIsNone(self._vote_user_field.default)

    def test_user_fk_related_name(self):
        related_name = getattr(
            self._vote_user_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'votes')

    # Test candidate foreign key.
    def test_candidate_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._vote_candidate_field, models.ForeignKey)
        )

    def test_candidate_fk_connected_model(self):
        connected_model = getattr(
            self._vote_candidate_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Candidate)

    def test_candidate_fk_on_delete(self):
        on_delete_policy = getattr(
            self._vote_candidate_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_candidate_fk_null(self):
        self.assertFalse(self._vote_candidate_field.null)

    def test_candidate_fk_blank(self):
        self.assertFalse(self._vote_candidate_field.blank)

    def test_candidate_fk_default(self):
        self.assertIsNone(self._vote_candidate_field.default)

    def test_candidate_fk_related_name(self):
        related_name = getattr(
            self._vote_candidate_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'votes')

    # Test vote_cipher field.
    def test_cipher_is_json_field(self):
        self.assertTrue(
            isinstance(self._vote_cipher_field, postgres_fields.JSONField)
        )

    def test_cipher_null(self):
        self.assertFalse(self._vote_cipher_field.null)

    def test_cipher_blank(self):
        self.assertFalse(self._vote_cipher_field.blank)

    def test_cipher_default(self):
        self.assertIsNone(self._vote_cipher_field.default)

    def test_cipher_unique(self):
        self.assertTrue(self._vote_cipher_field.unique)

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._vote._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'user', 'candidate' ])

    def test_meta_ordering(self):
        ordering = self._vote._meta.ordering
        self.assertEquals(
            ordering,
            [
                'candidate__position__position_level',
                'user__last_name',
                'user__first_name'
            ]
        )

    def test_meta_verbose_name(self):
        verbose_name = self._vote._meta.verbose_name
        self.assertEquals(verbose_name, 'vote')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._vote._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'votes')

    def test_str(self):
        self.assertEquals(str(self._vote), '<Vote for \'juan\' by \'juan\'>')


class CandidateTest(TestCase):
    """
    Tests the Candidate model.

    The Candidate model must have the following custom fields:
        - user_id (foreign key)
        - party_id (foreign key)
        - position_id (foreign key)

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The user field must be a one-to-one field and have the following
    settings:
        - to = 'User'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - related_name = '+' (it doesn't make sense to have a reverse
                              relationship in an is-a relationship)

    The party must be a foreign key and have the following settings:
        - to = 'CandidateParty'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidates'

    The position must be a foreign key and have the following settings:
        - to = 'CandidatePosition'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidates'

    The model must have the following meta settings:
        - Index must be set to the user field.
        - The ordering must be based on the position level first, then
          the user's last name, and lastly, the user's first name.
        - The singular verbose name will be "candidate", with the plural being
          "candidates".

    The __str__() method should return
    "<Candidate '{candidate username}' ('{position}' candidate of '{party}')>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Emerald')
        cls._user = User.objects.create(
            username='juan',
            batch=cls._batch,
            section=cls._section
        )
        cls._party = CandidateParty.objects.create(party_name='Awesome Party')
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._candidate = Candidate.objects.create(
            user=cls._user,
            party=cls._party,
            position=cls._position
        )
        cls._candidate_user_field = cls._candidate._meta.get_field('user')
        cls._candidate_party_field = cls._candidate._meta.get_field('party')
        cls._candidate_position_field = cls._candidate._meta.get_field(
            'position'
        )

    # Test user foreign key.
    def test_user_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_user_field, models.ForeignKey)
        )

    def test_user_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_user_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, User)

    def test_user_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_user_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_user_fk_null(self):
        self.assertFalse(self._candidate_user_field.null)

    def test_user_fk_blank(self):
        self.assertFalse(self._candidate_user_field.blank)

    def test_user_fk_default(self):
        self.assertIsNone(self._candidate_user_field.default)

    def test_user_fk_related_name(self):
        related_name = getattr(
            self._candidate_user_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, '+')

    # Test party foreign key.
    def test_party_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_party_field, models.ForeignKey)
        )

    def test_party_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_party_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, CandidateParty)

    def test_party_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_party_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_party_fk_null(self):
        self.assertFalse(self._candidate_party_field.null)

    def test_party_fk_blank(self):
        self.assertFalse(self._candidate_party_field.blank)

    def test_party_fk_default(self):
        self.assertIsNone(self._candidate_party_field.default)

    def test_party_fk_unique(self):
        self.assertFalse(self._candidate_party_field.unique)

    def test_party_fk_related_name(self):
        related_name = getattr(
            self._candidate_party_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidates')

    # Test position foreign key.
    def test_position_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_position_field, models.ForeignKey)
        )

    def test_position_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_position_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, CandidatePosition)

    def test_position_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_position_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_position_fk_null(self):
        self.assertFalse(self._candidate_position_field.null)

    def test_position_fk_blank(self):
        self.assertFalse(self._candidate_position_field.blank)

    def test_position_fk_default(self):
        self.assertIsNone(self._candidate_position_field.default)

    def test_position_fk_unique(self):
        self.assertFalse(self._candidate_position_field.unique)

    def test_party_fk_related_name(self):
        related_name = getattr(
            self._candidate_position_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidates')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._candidate._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'user' ])

    def test_meta_ordering(self):
        ordering = self._candidate._meta.ordering
        self.assertEquals(
            ordering,
            [
                'position__position_level',
                'user__last_name',
                'user__first_name'
            ]
        )

    def test_meta_verbose_name(self):
        verbose_name = self._candidate._meta.verbose_name
        self.assertEquals(verbose_name, 'candidate')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._candidate._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'candidates')

    def test_str(self):
        self.assertEquals(
            str(self._candidate),
            '<Candidate \'juan\' '
            + '(\'Amazing Position\' candidate of \'Awesome Party\'>'
        )


class CandidatePartyTest(TestCase):
    """
    Test the CandidateParty model.

    The CandidateParty model must have the following custom field:
        - party_name

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The party_name field must be a variable character field and have the
    following settings:
        - max_length = 32
        - null = False
        - blank = False
        - default = None
        - unique = True

    The model must have the following meta settings:
        - Index must be set to the party_name field.
        - The ordering must be alphabetical and be based on the party_name
          field.
        - The singular verbose name will be "party", with the plural being
          "parties".

    The __str___() method should return "<CandidateParty '{party name}'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._party = CandidateParty.objects.create(party_name='Awesome Party')
        cls._party_name_field = cls._party._meta.get_field('party_name')

    # Test party_name field.
    def test_party_name_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._party_name_field, models.CharField)
        )

    def test_party_name_max_length(self):
        self.assertEquals(self._party_name_field.max_length, 32)

    def test_party_name_null(self):
        self.assertFalse(self._party_name_field.null)

    def test_party_name_blank(self):
        self.assertFalse(self._party_name_field.blank)

    def test_party_name_default(self):
        self.assertIsNone(self._party_name_field.default)

    def test_party_name_unique(self):
        self.assertTrue(self._party_name_field.unique)

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._party._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'party_name' ])

    def test_meta_ordering(self):
        self.assertEquals(self._party._meta.ordering, [ 'party_name' ])

    def test_meta_verbose_name(self):
        self.assertEquals(self._party._meta.verbose_name, 'party')

    def test_meta_verbose_name_plural(self):
        self.assertEquals(self._party._meta.verbose_name_plural, 'parties')

    def test_str(self):
        self.assertEquals(
            str(self._party),
            '<CandidateParty \'Awesome Party\'>'
        )


class CandidatePositionTest(TestCase):
    """
    Test the CandidatePosition model.

    The CandidatePosition model must have the following custom fields:
        - position_name
        - position_level (a lower number means a higher position)

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The position_name field must be variable character field and have the
    following settings:
        - max_length = 32
        - null = False
        - blank = False
        - default = None
        - unique = True

    The position_level field must be a positive small integer field and
    have the following settings:
        - null = False
        - blank = False
        - default = 32767 (the largest number this field type supports)
        - unique = False

    The model must have the following meta settings:
        - Index must be set to the position_name field.
        - The ordering must be alphabetical and be based on the position_level
          field, then the position_name.
        - The singular verbose name will be "candidate position", with the
          plural for being "candidate positions".

    The __str___() method should return
    "<CandidatePosition '{position name}' (level {position level})>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        cls._position_name_field = cls._position._meta.get_field(
            'position_name'
        )
        cls._position_level_field = cls._position._meta.get_field(
            'position_level'
        )

    # Test position_name field.
    def test_position_name_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._position_name_field, models.CharField)
        )

    def test_position_name_max_length(self):
        self.assertEquals(self._position_name_field.max_length, 32)

    def test_position_name_null(self):
        self.assertFalse(self._position_name_field.null)

    def test_position_name_blank(self):
        self.assertFalse(self._position_name_field.blank)

    def test_position_name_default(self):
        self.assertIsNone(self._position_name_field.default)

    def test_position_name_unique(self):
        self.assertTrue(self._position_name_field.unique)

    # Test position level field.
    def test_position_level_is_positive_smallint_field(self):
        self.assertTrue(
            isinstance(
                self._position_level_field,
                models.PositiveSmallIntegerField
            )
        )

    def test_position_level_null(self):
        self.assertFalse(self._position_level_field.null)

    def test_position_level_blank(self):
        self.assertFalse(self._position_level_field.blank)

    def test_position_level_default(self):
        self.assertEquals(self._position_level_field.default, 32767)

    def test_position_level_unique(self):
        self.assertFalse(self._position_level_field.unique)

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._position._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'position_name' ])

    def test_meta_ordering(self):
        self.assertEquals(
            self._position._meta.ordering,
            [ 'position_level', 'position_name' ]
        )

    def test_meta_verbose_name(self):
        self.assertEquals(
            self._position._meta.verbose_name,
            'candidate position'
        )

    def test_meta_verbose_name_plural(self):
        self.assertEquals(
            self._position._meta.verbose_name_plural,
            'candidate positions'
        )

    def test_str(self):
        self.assertEquals(
            str(self._position),
            '<CandidatePosition \'{Amazing Position}\' (level 0)>'
        )


class ElectionSettingTest(TestCase):
    """
    Tests the ElectionSetting model.

    The ElectionSetting model must have the follwwing custom fields:
        - key
        - value

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The key field must be a variable character field and have the following
    settings:
        - max_length = 30
        - null = False
        - blank = False
        - default = None
        - unique = True

    The value field must be a text field and have the following settings:
        - null = True
        - blank = True
        - default = None
        - unique = False

    The reason why the value field must be a text field is that we might need
    to store JSON data in the settings. Sure, we can use a JSON field for this
    field. However, that would mean that other values that do not need to be
    stored as JSON will be stored as JSON, which will be completely
    unnecessary. We use a text field instead as a compromise between variable
    character fields and JSON fields. Variable character fields are not
    considered since they have a length restriction and JSON data do not always
    fit in the length restrictions you have set for the fields.

    The model must have the following meta settings:
        - Index must be set to the key field.
        - The ordering must be alphabetical and be based on the key field.
        - The singular verbose name will be "election setting", with the
          plural form being "election settings".

    The __str___() method should return value of the value field.
    """
    @classmethod
    def setUpTestData(cls):
        cls._setting = ElectionSetting.objects.create(
            key='test_key',
            value='test_value'
        )
        cls._setting_key_field = cls._setting._meta.get_field('key')
        cls._setting_value_field = cls._setting._meta.get_field('value')

    # Test key field.
    def test_key_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._setting_key_field, models.CharField)
        )

    def test_key_max_length(self):
        self.assertEquals(self._setting_key_field.max_length, 30)

    def test_key_null(self):
        self.assertFalse(self._setting_key_field.null)

    def test_key_blank(self):
        self.assertFalse(self._setting_key_field.blank)

    def test_key_default(self):
        self.assertIsNone(self._setting_key_field.default)

    def test_key_unique(self):
        self.assertTrue(self._setting_key_field.unique)

    def test_key_verbose_name(self):
        self.assertEquals(
            self._setting_key_field.verbose_name,
            'key'
        )

    # Test value field.
    def test_value_is_text_field(self):
        self.assertTrue(
            isinstance(self._setting_value_field, models.TextField)
        )

    def test_value_null(self):
        self.assertTrue(self._setting_value_field.null)

    def test_value_blank(self):
        self.assertTrue(self._setting_value_field.blank)

    def test_value_default(self):
        self.assertIsNone(self._setting_value_field.default)

    def test_value_unique(self):
        self.assertFalse(self._setting_value_field.unique)

    def test_value_verbose_name(self):
        self.assertEquals(
            self._setting_value_field.verbose_name,
            'value'
        )

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._setting._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'key' ])

    def test_meta_ordering(self):
        self.assertEquals(self._setting._meta.ordering, [ 'key' ])

    def test_meta_verbose_name(self):
        self.assertEquals(self._setting._meta.verbose_name, 'election setting')

    def test_meta_verbose_name_plural(self):
        self.assertEquals(
            self._setting._meta.verbose_name_plural,
            'election settings'
        )

    def test_str(self):
        self.assertEquals(str(self._setting), 'test_value')
