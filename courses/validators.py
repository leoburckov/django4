from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    Для PATCH запросов: если значение пустое, значит поле не обновлялось - пропускаем валидацию
    """
    # Разрешаем пустые значения (для PATCH запросов, когда поле не обновляется)
    if value is None or value == '':
        return value  # Разрешаем пустое значение

    # Если значение не пустое, но состоит только из пробелов
    if isinstance(value, str) and not value.strip():
        return value  # Разрешаем пустую строку

    # Только для непустых значений проводим YouTube валидацию
    try:
        parsed_url = urlparse(value)

        # Проверяем, что это HTTP/HTTPS ссылка
        if parsed_url.scheme not in ['http', 'https']:
            raise ValidationError('Разрешены только HTTP/HTTPS ссылки')

        # Проверяем домен
        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']
        domain = parsed_url.netloc.lower()

        # Проверяем все разрешенные домены
        domain_allowed = False
        for allowed_domain in allowed_domains:
            if domain == allowed_domain or domain.endswith('.' + allowed_domain):
                domain_allowed = True
                break

        if not domain_allowed:
            raise ValidationError(
                f'Ссылка должна вести на youtube.com. Ваша ссылка: {domain}'
            )

        # Дополнительная проверка для youtu.be (короткие ссылки)
        if domain == 'youtu.be':
            # Проверяем, что есть идентификатор видео
            path = parsed_url.path.strip('/')
            if not path:
                raise ValidationError('Некорректная ссылка youtu.be')

        # Проверяем, что это не просто домен youtube.com без видео
        if domain in ['youtube.com', 'www.youtube.com']:
            if not parsed_url.path or parsed_url.path == '/':
                raise ValidationError('Некорректная ссылка на YouTube. Укажите конкретное видео')

        return value

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Некорректная ссылка: {str(e)}')

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Некорректная ссылка: {str(e)}')

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Некорректная ссылка: {str(e)}')

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Некорректная ссылка: {str(e)}')

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Некорректная ссылка: {str(e)}')


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field='video_url'):
        self.field = field

    def __call__(self, data):
        if isinstance(data, dict):
            value = data.get(self.field)
        else:
            value = data

        return validate_youtube_url(value)

    def __repr__(self):
        return f'YouTubeURLValidator(field={self.field})'