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
    user = Fields.ApplicationUserProperty(verbose_name=u'使用者', is_lock=True)
    user_name_proxy = Fields.StringProperty(verbose_name=u'使用者名稱')
    user_email_proxy = Fields.StringProperty(verbose_name=u'E-Mail')
    user_avatar_proxy = Fields.ImageProperty(verbose_name=u'頭像')
    telephone = Fields.StringProperty(verbose_name=u'電話', default=u'')
    mobile = Fields.StringProperty(verbose_name=u'手機', default=u'')
    sex = Fields.StringProperty(verbose_name=u'性別', default=u'保密')
    address_country = Fields.StringProperty(verbose_name=u'國家', default=u'')
    address_city = Fields.StringProperty(verbose_name=u'縣市', default=u'')
    address_district = Fields.StringProperty(verbose_name=u'鄉鎮', default=u'')
    address_detail = Fields.StringProperty(verbose_name=u'地址', default=u'')
    address_zip = Fields.StringProperty(verbose_name=u'郵遞區號', default=u'')

    birthday_year = Fields.IntegerProperty(verbose_name=u'出生年', default=0)
    birthday_month = Fields.IntegerProperty(verbose_name=u'出生月', default=0)
    birthday_day = Fields.IntegerProperty(verbose_name=u'出生日', default=0)
    referrals = Fields.StringProperty(verbose_name=u'推薦人', default=u'')
    is_referrals_change = Fields.BooleanProperty(verbose_name=u'推薦人已修改', default=False)

    mobile_verification_code = Fields.HiddenProperty(verbose_name=u'手機驗証碼', default=u'')
    is_mobile_verified = Fields.BooleanProperty(verbose_name=u'手機是否已驗証', default=False)
    need_verification_mobile = Fields.HiddenProperty(verbose_name=u'需驗証的手機', default=u'')
    last_verified_mobile = Fields.HiddenProperty(verbose_name=u'最後驗証成功的手機', default=u'')

    email_verification_code = Fields.HiddenProperty(verbose_name=u'信箱驗証碼', default=u'')
    is_email_verified_proxy = Fields.BooleanProperty(verbose_name=u'信箱是否已驗証', default=False)
    need_verification_email = Fields.HiddenProperty(verbose_name=u'需驗証的信箱', default=u'')
    last_verified_email = Fields.HiddenProperty(verbose_name=u'最後驗証成功的信箱', default=u'')

    address_verification_code = Fields.HiddenProperty(verbose_name=u'地址驗証碼', default=u'')
    is_address_verified = Fields.BooleanProperty(verbose_name=u'地址是否已驗証', default=False)

    @classmethod
    def get_or_create(cls, user):
        r = cls.query(cls.user==user.key).get()
        if r is None:
            r = cls(user=user.key)
            r.user_name_proxy = user.name
            r.user_email_proxy = user.email
            r.user_avatar_proxy = user.avatar
            r.is_email_verified_proxy = user.is_email_verified
            r.put()
        r._user = user
        r.password = r._user.password
        r.old_password = r._user.password
        return r

    @property
    def user_instance(self):
        if not hasattr(self, '_user'):
            self._user = self.user.get()
        return self._user

    def update_user(self, user=None):
        if user is None:
            user = self.user_instance
        if user is None:
            return

        if hasattr(self, 'old_password') and self.old_password != self.password:
            user.password = self.password
            user.bycrypt_password()
            self.password = user.password
            self.old_password = user.password
        try:
            user.name = self.user_name_proxy
            user.email = self.user_email_proxy
            user.avatar = self.user_avatar_proxy
            user.is_email_verified = self.is_email_verified_proxy
        except:
            pass
        user.put()

    @property
    def user_name(self):
        if self.user_instance:
            return self.user_instance.name
        return u'該帳號已被刪除'

    @user_name.setter
    def user_name(self, value):
        self.user_name_proxy = value

    @property
    def email(self):
        if self.user_instance:
            return self.user_instance.email
        return u''

    @email.setter
    def email(self, value):
        self.user_email_proxy = value

    @property
    def avatar(self):
        if self.user_instance:
            return self.user_instance.avatar
        return u''

    @avatar.setter
    def avatar(self, value):
        self.user_avatar_proxy = value

    @property
    def is_email_verified(self):
        if self.user_instance:
            return self.user_instance.is_email_verified
        return False

    @is_email_verified.setter
    def is_email_verified(self, value):
        self.is_email_verified_proxy = value

    @classmethod
    def after_get(cls, key, item):
        if item.user_instance:
            item.user_name_proxy = item.user_instance.name
            item.user_email_proxy = item.user_instance.email
            item.user_avatar_proxy = item.user_instance.avatar
            item.is_email_verified_proxy = item.user_instance.is_email_verified
        else:
            item.user_name_proxy = u'該帳號已被刪除'

    def gen_email_verification_code(self, email):
        import random, string
        r = ''.join(random.choice(string.lowercase) for i in range(25))
        self.need_verification_email = email
        self.email_verification_code = u'%s-%s-%s-%s' % (r[0:4], r[5:9], r[10:14], r[15:19])

    def gen_mobile_verification_code(self, mobile):
        import random
        self.need_verification_mobile = mobile
        self.mobile_verification_code = u'%s' % (random.randint(100000, 999999))

    def verify_email(self, code):
        if self.email_verification_code == code:
            self.last_verified_email = self.need_verification_email
            self.is_email_verified_proxy = True
            self.user_email_proxy = self.last_verified_email
            self.user_instance.email = self.last_verified_email
            self.user_instance.is_email_verified = True
            self.user_instance.put()
            self.email_verification_code = ''
            self.put()
            return True
        return False

    def verify_mobile(self, code):
        if self.mobile_verification_code == code:
            self.last_verified_mobile = self.need_verification_mobile
            self.is_mobile_verified = True
            self.mobile_verification_code = ''
            self.put()
            return True
        return False

    @property
    def birthday(self):
        return '%d-%02d-%02d' % (self.birthday_year, self.birthday_month, self.birthday_day)
