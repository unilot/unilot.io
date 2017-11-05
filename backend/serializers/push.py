from collections import OrderedDict

from rest_framework import serializers
from django.utils.translation import activate, ugettext as _

from sportloto.settings import LANGUAGES


class PushAction():
    GAME_STARTED = 'game_started'
    GAME_UPDATED = 'game_updated'
    GAME_UNPUBLISHED = 'game_unpublished'
    GAME_FINISHED = 'game_finished'


class GameAsPayloadMixin():
    def __message_init__(self, *args, **kwargs):
        from backend.models import Game
        from backend.serializers.game import PublicGameSerializer

        payload = kwargs.pop('payload', None)

        if not isinstance(payload, Game):
            raise AttributeError('payload should be instance of Game model')

        serializer = PublicGameSerializer(payload)

        data = kwargs.get('data', {})

        # Data field in payload
        data['data'] = OrderedDict(serializer.data)

        kwargs['data'] = data

        return (args, kwargs)


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
