# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Table
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Assignment(db.Model):
    __tablename__ = 'assignment'

    team_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))



class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    description = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)



class Guest(db.Model):
    __tablename__ = 'guest'

    id = db.Column(db.Integer, primary_key=True)
    ota_guest_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    first_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    last_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    phone = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    email = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    source = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    country_code = db.Column(db.String(3, u'utf8mb4_unicode_ci'))
    gender = db.Column(db.String(10, u'utf8mb4_unicode_ci'))



class InternalChannel(db.Model):
    __tablename__ = 'internal_channel'

    id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String(100, u'utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    status = db.Column(db.ENUM(u'ACTIVE', u'DEACTIVE'), nullable=False)
    deleted_at = db.Column(db.DateTime)

    users = db.relationship(u'User', secondary=u'internal_channel_has_user', backref='internal_channels')



t_internal_channel_has_user = db.Table(
    'internal_channel_has_user',
    db.Column('internal_channel_id', db.ForeignKey(u'internal_channel.id'), primary_key=True, nullable=False, index=True),
    db.Column('user_id', db.ForeignKey(u'user.id'), primary_key=True, nullable=False, index=True)
)



class InternalMessage(db.Model):
    __tablename__ = 'internal_message'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    internal_channel_id = db.Column(db.ForeignKey(u'internal_channel.id'), primary_key=True, nullable=False, index=True)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    internal_channel = db.relationship(u'InternalChannel', primaryjoin='InternalMessage.internal_channel_id == InternalChannel.id', backref='internal_messages')



class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)



class Listing(db.Model):
    __tablename__ = 'listing'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.ForeignKey(u'team.id'), nullable=False, index=True)
    name = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(256))
    country_code = db.Column(db.String(3, u'utf8mb4_unicode_ci'), nullable=False)
    bedrooms = db.Column(db.Integer)
    notes = db.Column(db.String)
    internal_name = db.Column(db.String(45))
    timezone_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    property_type = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    summary = db.Column(db.String)
    primary_host_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    primary_host_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    status = db.Column(db.ENUM(u'ACTIVATE', u'DEACTIVATE'))
    check_in_time = db.Column(db.Integer)
    check_out_time = db.Column(db.Integer)
    check_in_time_ends_at = db.Column(db.Integer)
    property_privacy = db.Column(db.String(collation=u'utf8mb4_unicode_ci'))
    source = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    ota_listing_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)

    team = db.relationship(u'Team', primaryjoin='Listing.team_id == Team.id', backref='listings')
    teams = db.relationship(u'TeamMember', secondary=u'team_member_has_listing', backref='listings')



class ListingHasTemplate(db.Model):
    __tablename__ = 'listing_has_template'

    listing_id = db.Column(db.ForeignKey(u'listing.id'), primary_key=True, nullable=False, index=True)
    template_id = db.Column(db.ForeignKey(u'template.id'), primary_key=True, nullable=False, index=True)
    event_id = db.Column(db.ForeignKey(u'event.id'), primary_key=True, nullable=False, index=True)
    condition = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    tactics = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    time_before = db.Column(db.Integer)
    time_after = db.Column(db.Integer)

    event = db.relationship(u'Event', primaryjoin='ListingHasTemplate.event_id == Event.id', backref='listing_has_templates')
    listing = db.relationship(u'Listing', primaryjoin='ListingHasTemplate.listing_id == Listing.id', backref='listing_has_templates')
    template = db.relationship(u'Template', primaryjoin='ListingHasTemplate.template_id == Template.id', backref='listing_has_templates')



class ListingImage(db.Model):
    __tablename__ = 'listing_image'

    listing_id = db.Column(db.ForeignKey(u'listing.id'), nullable=False, index=True)
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.ENUM(u'small', u'medium', u'large'))
    type = db.Column(db.ENUM(u'cover', u'thumbnail'))
    caption = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    listing = db.relationship(u'Listing', primaryjoin='ListingImage.listing_id == Listing.id', backref='listing_images')



class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.ForeignKey(u'thread.id'), nullable=False, index=True)
    ota_thread_id = db.Column(db.String(100, u'utf8mb4_unicode_ci'))
    ota_message_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    hash_key = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    language = db.Column(db.String(3, u'utf8mb4_unicode_ci'))
    check_in_date = db.Column(db.DateTime)
    check_out_date = db.Column(db.DateTime)
    sender_id = db.Column(db.String(100, u'utf8mb4_unicode_ci'))
    sender_type = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    status = db.Column(db.ENUM(u'PENDING', u'SENT', u'DELETED'))
    content_in_en = db.Column(db.String)
    reservation_code = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    reply_to_email = db.Column(db.String(45, u'utf8mb4_unicode_ci'))

    thread = db.relationship(u'Thread', primaryjoin='Message.thread_id == Thread.id', backref='messages')



class OtaAccount(db.Model):
    __tablename__ = 'ota_account'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.ForeignKey(u'team.id'), nullable=False, index=True)
    user_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    email = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    password = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    source = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    token = db.Column(db.String(100, u'utf8mb4_unicode_ci'))
    status = db.Column(db.ENUM(u'ACTIVATE', u'DEACTIVATE'), nullable=False)
    last_login = db.Column(db.DateTime)
    link_url = db.Column(db.String(200, u'utf8mb4_unicode_ci'))

    team = db.relationship(u'Team', primaryjoin='OtaAccount.team_id == Team.id', backref='ota_accounts')



class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.ForeignKey(u'thread.id'), nullable=False, index=True)
    ota_listing_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    check_in_date = db.Column(db.DateTime)
    check_out_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    reservation_code = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    status = db.Column(db.ENUM(u'ACTIVATE', u'DEACTIVATE'), nullable=False)
    check_in_time = db.Column(db.Integer)
    check_out_time = db.Column(db.Integer)
    flight_number = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    note = db.Column(db.String(collation=u'utf8mb4_unicode_ci'))
    source = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    earning = db.Column(db.Integer)
    commission = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    earning_currency = db.Column(db.String(4, u'utf8mb4_unicode_ci'))

    thread = db.relationship(u'Thread', primaryjoin='Reservation.thread_id == Thread.id', backref='reservations')



class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    general_rating = db.Column(db.Integer)
    accuracy_rating = db.Column(db.Integer)
    check_in_rating = db.Column(db.Integer)
    cleanliness_rating = db.Column(db.Integer)
    value_rating = db.Column(db.Integer)
    location_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    private_feedback = db.Column(db.String)
    reservation_id = db.Column(db.ForeignKey(u'reservation.id'), nullable=False, index=True)
    ota_review_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    hash_key = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    modified_at = db.Column(db.DateTime)

    reservation = db.relationship(u'Reservation', primaryjoin='Review.reservation_id == Reservation.id', backref='reviews')



class ScheduledMesssage(db.Model):
    __tablename__ = 'scheduled_messsage'
    __table_args__ = (
        db.ForeignKeyConstraint(['listing_id', 'template_id', 'event_id'], [u'listing_has_template.listing_id', u'listing_has_template.template_id', u'listing_has_template.event_id']),
        db.Index('fk_scheduled_messsage__listing_has_template__idx', 'listing_id', 'template_id', 'event_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.ENUM(u'ACITIVATE', u'DEACTIVATE'))
    will_send_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    listing_id = db.Column(db.Integer, nullable=False)
    template_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    thread_id = db.Column(db.ForeignKey(u'thread.id'), nullable=False, index=True)

    listing = db.relationship(u'ListingHasTemplate', primaryjoin='and_(ScheduledMesssage.listing_id == ListingHasTemplate.listing_id, ScheduledMesssage.template_id == ListingHasTemplate.template_id, ScheduledMesssage.event_id == ListingHasTemplate.event_id)', backref='scheduled_messsages')
    thread = db.relationship(u'Thread', primaryjoin='ScheduledMesssage.thread_id == Thread.id', backref='scheduled_messsages')



class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.ForeignKey(u'user.id'), nullable=False, index=True)
    name = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    status = db.Column(db.ENUM(u'PENDING', u'ACTIVATE', u'DEACTIVATE'), nullable=False)
    service_type = db.Column(db.ENUM(u'free', u'professional', u'ultimate'), nullable=False)
    email = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    about = db.Column(db.String(collation=u'utf8mb4_unicode_ci'))

    owner = db.relationship(u'User', primaryjoin='Team.owner_id == User.id', backref='teams')



class TeamMember(db.Model):
    __tablename__ = 'team_member'

    team_id = db.Column(db.ForeignKey(u'team.id'), primary_key=True, nullable=False, index=True)
    user_id = db.Column(db.ForeignKey(u'user.id'), primary_key=True, nullable=False, index=True)
    role = db.Column(db.ENUM(u'host', u'cohost', u'cleaner'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    team = db.relationship(u'Team', primaryjoin='TeamMember.team_id == Team.id', backref='team_members')
    user = db.relationship(u'User', primaryjoin='TeamMember.user_id == User.id', backref='team_members')



t_team_member_has_listing = db.Table(
    'team_member_has_listing',
    db.Column('team_id', db.Integer, primary_key=True, nullable=False),
    db.Column('user_id', db.Integer, primary_key=True, nullable=False),
    db.Column('listing_id', db.ForeignKey(u'listing.id'), primary_key=True, nullable=False, index=True),
    db.ForeignKeyConstraint(['team_id', 'user_id'], [u'team_member.team_id', u'team_member.user_id']),
    db.Index('fk_team_member_has_listing__team_member__idx', 'team_id', 'user_id')
)



class Template(db.Model):
    __tablename__ = 'template'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(45), nullable=False)
    language = db.Column(db.String(5, u'utf8mb4_unicode_ci'), nullable=False)
    team_id = db.Column(db.ForeignKey(u'team.id'), nullable=False, index=True)
    target = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    team = db.relationship(u'Team', primaryjoin='Template.team_id == Team.id', backref='templates')



class Thread(db.Model):
    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.ForeignKey(u'listing.id'), nullable=False, index=True)
    latest_reservation_id = db.Column(db.Integer, nullable=False)
    ota_listing_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    source = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    status = db.Column(db.ENUM(u'NORMAL', u'CANCELLED'))
    ota_thread_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    reply_to_email = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    main_language = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    guest_id = db.Column(db.ForeignKey(u'guest.id'), nullable=False, index=True)

    guest = db.relationship(u'Guest', primaryjoin='Thread.guest_id == Guest.id', backref='threads')
    listing = db.relationship(u'Listing', primaryjoin='Thread.listing_id == Listing.id', backref='threads')



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    last_name = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    about = db.Column(db.String)
    email = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False, unique=True)
    phone = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    country_code = db.Column(db.String(3, u'utf8mb4_unicode_ci'))
    location = db.Column(db.String(100, u'utf8mb4_unicode_ci'))
    password_hash = db.Column(db.String(300, u'utf8mb4_unicode_ci'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    status = db.Column(db.ENUM(u'ACTIVATED', u'PENDING', u'DEACTIVATED'))
    score = db.Column(db.Integer, server_default=db.FetchedValue())
    identity_verified = db.Column(db.Integer)
    role = db.Column(db.String(45, u'utf8mb4_unicode_ci'), nullable=False)
    languages = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    auth0_user_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    sendbird_id = db.Column(db.String(45, u'utf8mb4_unicode_ci'))
    thread_slack_id = db.Column(db.String(50, u'utf8mb4_unicode_ci'))
    avatar = db.Column(db.String(collation=u'utf8mb4_unicode_ci'))



class UserImage(db.Model):
    __tablename__ = 'user_image'

    user_id = db.Column(db.ForeignKey(u'user.id'), nullable=False, index=True)
    size = db.Column(db.ENUM(u'small', u'medium', u'large'), nullable=False)
    type = db.Column(db.ENUM(u'profile', u'thumbnail'))
    caption = db.Column(db.String(256, u'utf8mb4_unicode_ci'))
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship(u'User', primaryjoin='UserImage.user_id == User.id', backref='user_images')
