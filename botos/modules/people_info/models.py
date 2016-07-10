# botos/modules/people_info/models.py
# Copyright (C) 2016 Sean Francis N. Ballais
#
# This module is part of Botos and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Models that will be used throughout the app

"""


from botos import db


class Base(db.Model):
    """The class that all models inherit from. Not to be used directly."""

    __abstract__  = True

    id             = db.Column(db.Integer,
                               primary_key=True,
                               unique=True
                               )
    date_created   = db.Column(db.DateTime,
                               default=db.func.current_timestamp()
                               )
    date_modified  = db.Column(db.DateTime,
                               default=db.func.current_timestamp(),
                               onupdate=db.func.current_timestamp()
                               )


class User(Base):
    """Represents the voter in the database. Voter is deleted after voting."""
    __tablename__  = 'voter'

    username       = db.Column(db.String(8),
                               nullable=False,
                               unique=True
                               )
    password       = db.Column(db.String(128),
                               nullable=False
                               )
    section_id     = db.Column(db.Integer,
                               db.ForeignKey('section.id')
                               )
    role           = db.Column(db.String(8),
                               nullable=False
                               )

    def __init__(self,
                 username,
                 password,
                 section_id,
                 role
                 ):
        """
        Construct a new ''Voter'' object.

        :param username: The username of the voter. Voter usernames are
            8-character long combination of alphanumeric and special
            characters. IDs are automatically generated by the app.
        :param password: The password of the voter. Passwords are
            12-character long combination of alphanumeric and special
            characters that are hashed and salted using the SHA-512 hash
            function. Passwords are automatically generated by the app.
        :param section_id: The id of the section the voter is assigned to.
            The sections are used to group statistical data. Optional for admins.
        :param role: Role of the user whether he is a voter, admin, or viewer.
        """
        self.username      = username
        self.password      = password
        self.section_id    = section_id
        self.role          = role

    def is_authenticated(self):
        """
        Check if the voter has been authenticated already.

        :return: True if the voter is already authenticated.
        """
        return True

    def is_active(self):
        """
        Check if the user has already finished voting.

        :return: True if the voter has not voted yet.
        """
        return True

    def is_anonymous(self):
        """
        Check if the user has logged in already.

        :return: False if the voter has logged in.
        """
        return False

    def get_user(self):
        """
        Get the ID of the user.

        :return: The username of the user with respect to the database.
        """
        return str(self.id,
                   'utf-8'
                   )

    def __repr__(self):
        return '<Voter %r>' % self.id


class VoterSection(Base):
    """Represents the sections of the voters in the database."""
    __tablename__  = 'voter_section'

    section_name   = db.Column(db.String(16),
                               nullable=False,
                               unique=True
                               )
    batch_id       = db.Column(db.Integer,
                               db.ForeignKey('batch.id')
                               )
    voter_section  = db.relationship('User',
                                     backref=db.backref('section',
                                                        lazy='select'
                                                        ),
                                     lazy='dynamic'
                                     )
    section_votes  = db.relationship('VoterSectionVotes',
                                     backref=db.backref('section',
                                                        lazy='select'
                                                        ),
                                     lazy='dynamic'
                                     )

    def __init__(self,
                 section_name,
                 section_batch
                 ):
        """
        Construct a new ''VoterSection'' object.
        :param section_name: The name of the section. The section are used
            are used to group statistical data.
        :param section_batch: The batch the section is under.
        """
        self.section_name  = section_name
        self.section_batch = section_batch

    def __repr__(self):
        return '<VoterSection %r>' % self.section_name


class VoterBatch(Base):
    """Represents the batches of the voters in the database."""
    __tablename__   = 'voter_batch'

    batch_name      = db.Column(db.String(16),
                                nullable=False,
                                unique=True
                                )
    batch_sections  = db.relationship('VoterSection',
                                      backref=db.backref('batch',
                                                         lazy='select'
                                                         ),
                                      lazy='dynamic'
                                      )

    def __init__(self,
                 batch_name
                 ):
        """
        Construct a new ''VoterBatch'' object.

        :param batch_name: The name of the batch. This may be a year, an
            actual batch name, or any random character combination of
            16 characters in length.
        """
        self.batch_name = batch_name

    def __repr__(self):
        return '<VoterBatch %r>' % self.batch_year


class Candidate(Base):
    """Represents the candidate in the database."""
    __tablename__   = 'candidate'

    candidate_id    = db.Column(db.Integer,
                                nullable=False,
                                autoincrement=True
                                )

    candidate_idx   = db.Column(db.SmallInteger,
                                nullable=False
                                )  # Index that will be used for the positioning in the voting page
    first_name      = db.Column(db.String(16),
                                nullable=False
                                )
    last_name       = db.Column(db.String(16),
                                nullable=False
                                )
    middle_name     = db.Column(db.String(16),
                                nullable=True
                                )
    position        = db.Column(db.Integer,
                                db.ForeignKey('candidate_position.id')
                                )
    party           = db.Column(db.Integer,
                                db.ForeignKey('candidate_party.id')
                                )

    def __init__(self,
                 candidate_idx,
                 first_name,
                 last_name,
                 position,
                 party,
                 middle_name=''
                 ):
        """
        Construct a new ''Candidate'' object.

        :param candidate_idx: The index of the candidate with respect to the voting page position
        :param first_name: The first name of the candidate.
        :param last_name: The surname of the candidate.
        :param middle_name: The middle name of the candidate.
        :param position: The position a candidate is holding.
        :param party: The party in which a candidate belongs to.
        """
        self.candidate_idx   = candidate_idx
        self.first_name      = first_name
        self.last_name       = last_name
        self.middle_name     = middle_name
        self.position        = position
        self.party           = party

    def __repr__(self):
        return '<Candidate %r>' % (self.first_name + self.last_name)


class CandidatePosition(Base):
    """Represents the candidate positions in the database."""
    __tablename__   = 'candidate_position'

    name            = db.Column(db.String(32),
                                nullable=False,
                                unique=True
                                )
    level           = db.Column(db.SmallInteger,
                                nullable=False
                                )  # Level is like the hierarchy level of the candidate
    candidates      = db.relationship('Candidate',
                                      backref=db.backref('candidate_position',
                                                         lazy='select'
                                                         ),
                                      lazy='dynamic'
                                      )

    def __init__(self,
                 name,
                 level
                 ):
        """
        Construct a new ''CandidatePosition'' object.

        :param name: Name of the candidate position
        :param level: The level of the position.
        """
        self.name  = name
        self.level = level

    def __repr__(self):
        return '<CandidatePosition %r>' % self.name


class CandidateParty(Base):
    """Represents the candidate party in the database."""
    __tablename__   = 'candidate_party'

    name            = db.Column(db.String(16),
                                nullable=False,
                                unique=True
                                )
    candidates      = db.relationship('Candidate',
                                      backref=db.backref('candidate_party',
                                                         lazy='select'),
                                      lazy='dynamic'
                                      )

    def __init__(self,
                 name
                 ):
        """
        Construct a new ''CandidateParty'' object.

        :param name: The name of the Candidate party.
        """
        self.name = name

    def __repr__(self):
        return '<CandidateParty %r>' % self.name