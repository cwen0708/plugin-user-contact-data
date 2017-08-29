#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.

from argeweb import BasicModel
from argeweb import Fields
from plugins.application_user.models.application_user_model import ApplicationUserModel


class UserContactDataModel(BasicModel):
    name = Fields.StringProperty(verbose_name=u'識別名稱')
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    user_name_proxy = Fields.StringProperty(verbose_name=u'使用者名稱')
    user_email_proxy = Fields.StringProperty(verbose_name=u'E-Mail')
    user_avatar_proxy = Fields.ImageProperty(verbose_name=u'頭像')
    telephone = Fields.StringProperty(verbose_name=u'電話', default=u'')
    mobile = Fields.StringProperty(verbose_name=u'手機', default=u'')
    address_country = Fields.StringProperty(verbose_name=u'國家', default=u'')
    address_city = Fields.StringProperty(verbose_name=u'縣市', default=u'')
    address_district = Fields.StringProperty(verbose_name=u'鄉鎮', default=u'')
    address_detail = Fields.StringProperty(verbose_name=u'地址', default=u'')
    address_zip = Fields.StringProperty(verbose_name=u'郵遞區號', default=u'')

    @classmethod
    def get_or_create(cls, user):
        r = cls.query(cls.user==user.key).get()
        if r is None:
            r = cls(user=user.key)
            r.put()
        r._user = user
        r.password = r._user.password
        r.old_password = r._user.password
        return r

    @classmethod
    def after_get(cls, key, item):
        super(UserContactDataModel, cls).after_get(key, item)
        item.password = item.user_instance.password
        item.old_password = item.user_instance.password
        item.user_name_proxy = item.user_instance.name
        item.user_email_proxy = item.user_instance.email
        item.user_avatar_proxy = item.user_instance.avatar

    @property
    def user_instance(self):
        if not hasattr(self, '_user'):
            self._user = self.user.get()
        return self._user

    def after_put(self, key):
        if hasattr(self, 'old_password') and self.old_password != self.password:
            self.user_instance.password = self.password
            self.user_instance.bycrypt_password()
            self.password = self.user_instance.password
            self.old_password = self.user_instance.password
        self.user_instance.name = self.user_name_proxy
        self.user_instance.email = self.user_email_proxy
        self.user_instance.avatar = self.user_avatar_proxy
        self.user_instance.put()

    @property
    def user_name(self):
        return self.user_instance.name

    @user_name.setter
    def user_name(self, value):
        self.user_name_proxy = value
        self.user_instance.name = value

    @property
    def email(self):
        return self.user_instance.email

    @email.setter
    def email(self, value):
        self.user_email_proxy = value
        self.user_instance.email = value

    @property
    def avatar(self):
        return self.user_instance.avatar

    @avatar.setter
    def avatar(self, value):
        self.user_avatar_proxy = value
        self.user_instance.avatar = value
