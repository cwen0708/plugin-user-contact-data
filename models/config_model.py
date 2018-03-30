#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/8/8.

from argeweb import BasicConfigModel
from argeweb import Fields


class ConfigModel(BasicConfigModel):
    title = Fields.HiddenProperty(verbose_name=u'設定名稱', default=u'聯絡資料相關設定')
    use_referrals = Fields.BooleanProperty(verbose_name=u'使用 推薦人 欄位', default=False)
    use_birthday = Fields.BooleanProperty(verbose_name=u'使用 出生日期 欄位', default=False)