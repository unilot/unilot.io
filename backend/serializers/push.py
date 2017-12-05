from collections import OrderedDict

from rest_framework import serializers
from django.utils.translation import activate, ugettext as _

from unilot.settings import LANGUAGES


class PushAction():
    GAME_STARTED = 'game_started'
    GAME_UPDATED = 'game_updated'
    GAME_UNPUBLISHED = 'game_unpublished'
    GAME_FINISHED = 'game_finished'
    GAME_CANCELED = 'game_canceled'

    ACTIONS_LIST = (GAME_STARTED,
                    GAME_UPDATED,
                    GAME_UNPUBLISHED,
                    GAME_FINISHED)
    CHOICES = (
        (GAME_STARTED, _('Game started')),
        (GAME_UPDATED, _('Game updated')),
        (GAME_UNPUBLISHED, _('Game unpublished')),
        (GAME_FINISHED, _('Game finished')),
    )


class GameAsPayloadMixin():
    __game__ = None

    def get_game(self):
        return self.__game__

    def __set_game(self, game):
        from backend.models import Game

        if not isinstance(game, Game):
            raise AttributeError('payload should be instance of Game model')

        self.__game__ = game

    def __message_init__(self, *args, **kwargs):
        from backend.serializers.game import PublicGameSerializer

        self.__set_game(kwargs.pop('payload', None))

        serializer = PublicGameSerializer(self.get_game())

        data = kwargs.get('data', {})

        # Data field in payload
        data['data'] = OrderedDict(serializer.data)

        kwargs['data'] = data

        return (args, kwargs)

    def is_matching_settings(self, settings):
        """
        :param settings:
        :type backend.models.DeviceSettings:
        """
        from backend.models import Game


        result = True
        game = self.get_game()

        if not settings.dayly_game_notifications_enabled and game.type == Game.TYPE_1_DAY:
            result = False
        elif not settings.weekly_game_notifications_enabled and game.type == Game.TYPE_7_DAYS:
            result = False
        elif not settings.bonus_game_notifications_enabled and game.type == Game.TYPE_30_DAYS:
            result = False

        return (result and super(GameAsPayloadMixin, self).is_matching_settings(settings))

    def get_required_settings(self):
        from backend.models import Game

        settings = {}
        game = self.get_game()

        if game.type == Game.TYPE_1_DAY:
            settings['dayly_game_notifications_enabled'] = True
        elif game.type == Game.TYPE_7_DAYS:
            settings['weekly_game_notifications_enabled'] = True
        elif game.type == Game.TYPE_30_DAYS:
            settings['bonus_game_notifications_enabled'] = True

        parent_result = {}

        if hasattr(super(GameAsPayloadMixin, self), 'get_required_settings'):
            parent_result = super(GameAsPayloadMixin, self).get_required_settings()

        return {**settings, **parent_result}


class PushMessage(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        n_args, n_kwargs = self.__message_init__(*args, **kwargs)

        super(PushMessage, self).__init__(*n_args, **n_kwargs)

    #Fields
    action = serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(method_name='build_message', read_only=True)
    data = serializers.DictField(required=True)

    def __message_init__(self, *args, **kwargs):
        return (args, kwargs)

    def build_message(self, *args, **kwarg):
        result = {}

        for language in LANGUAGES:
            lang_code, lang_name = language

            activate(lang_code)
            result[lang_code] = _(self.message_text())

        return result

    @staticmethod
    def message_text():
        raise NotImplementedError()

    def get_action(self, *args, **kwargs):
        raise NotImplementedError()

    def is_matching_settings(self, settings):
        return True

    def get_required_settings(self):
        settings = {}

        parent_result = {}

        if hasattr(super(PushMessage, self), 'get_required_settings'):
            parent_result = super(PushMessage, self).get_required_settings()

        return {**settings, **parent_result}


class GameUpdatedPushMessage(GameAsPayloadMixin, PushMessage):

    @staticmethod
    def message_text():
        return 'Game updated!'

    def get_action(self, *args, **kwargs):
        return PushAction.GAME_UPDATED


class GameUnpublishedPushMessage(GameAsPayloadMixin, PushMessage):

    @staticmethod
    def message_text():
        return 'Choice of winner started!'

    def get_action(self, *args, **kwargs):
        return PushAction.GAME_UNPUBLISHED


class GameFinishedPushMessage(PushMessage):

    def __message_init__(self, *args, **kwargs):
        from backend.models import Game

        payload = kwargs.pop('payload', None)

        if not isinstance(payload, Game):
            raise AttributeError('payload should be instance of Game model')

        game_data = {'data': {
                'id': payload.id,
                'type': payload.type,
                'winners': list(payload.get_winners().keys())
            }
        }

        data = kwargs.pop('data', {})

        data = {**data, **game_data}

        kwargs['data'] = data

        return super().__message_init__(*args, **kwargs)

    @staticmethod
    def message_text():
        return 'Game finished!'

    def get_action(self, *args, **kwargs):
        return PushAction.GAME_FINISHED


class GameStartedPushMessage(GameAsPayloadMixin, PushMessage):
    @staticmethod
    def message_text():
        return 'New Game Started!'

    def get_action(self, *args, **kwargs):
        return PushAction.GAME_STARTED
