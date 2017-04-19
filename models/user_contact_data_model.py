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
        item._user = item.user.get()
        item.password = item._user.password
        item.old_password = item._user.password
        item.user_name_proxy = item._user.name
        item.user_email_proxy = item._user.email
        item.user_avatar_proxy = item._user.avatar

    def after_put(self, key):
        if self.old_password != self.password:
            self._user.password = self.password
            self._user.bycrypt_password()
            self.password = self._user.password
            self.old_password = self._user.password
        self._user.name = self.user_name_proxy
        self._user.email = self.user_email_proxy
        self._user.avatar = self.user_avatar_proxy
        self._user.put()

    @property
    def user_name(self):
        return self._user.name

    @user_name.setter
    def user_name(self, value):
        self.user_name_proxy = value
        self._user.name = value

    @property
    def email(self):
        return self._user.email

    @email.setter
    def email(self, value):
        self.user_email_proxy = value
        self._user.email = value

    @property
    def avatar(self):
        return self._user.avatar

    @avatar.setter
    def avatar(self, value):
        self.user_avatar_proxy = value
        self._user.avatar = value
