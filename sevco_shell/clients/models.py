from enum import Enum
from functools import partial
import dacite

from dataclasses import asdict 
from datetime import datetime, timezone
from dacite.exceptions import MissingValueError, UnexpectedDataError

import dateutil.parser
from typing import Any, Dict, List, Tuple, Union

from enum import Enum


class HideValue(Enum):
    def __repr__(self):
        return '%s' % (self.name)


class OperatingSystem(HideValue):
    WINDOWS_AMD64 = 'WINDOWS_AMD64'
    DARWIN_AMD64 = 'DARWIN_AMD64'
    LINUX_AMD64 = 'LINUX_AMD64'


class ModelError(Exception):
    pass


class MissingRequiredFieldsError(ModelError):
    def __init__(self, field):
        super().__init__(f"Missing required field: {field}")

    @classmethod
    def from_dacite_error(cls, err: MissingValueError) -> 'MissingRequiredFieldsError':
        return cls(err.field_path)


class UnexpectedFieldError(ModelError):
    def __init__(self, field):
        super().__init__(f"Unexpected field: {field}")

    @classmethod
    def from_dacite_error(cls, err: UnexpectedDataError) -> 'UnexpectedFieldError':
        return cls(err.keys)


def _custom_dict_factory(convert_datetime: bool, tuples: List[Tuple[Any, Any]]) -> Dict:
    result = dict()
    for k, v in tuples:
        if convert_datetime and isinstance(v, datetime):
            result[k] = v.astimezone(timezone.utc).isoformat()
        elif isinstance(v, HideValue):
            result[k] = v.value
        else:
            result[k] = v

    return result


def dissolve_type(type_anno):
    if getattr(type_anno, '__origin__', None) is Union and type(None) in type_anno.__args__:
        # This is an Optional type
        return next(iter(a for a in type_anno.__args__ if a != type(None)))

    return type_anno


def parse_datetime(d):
    if isinstance(d, datetime):
        return d
    return dateutil.parser.isoparse(d)


class with_dict:
    @classmethod
    def from_dict(cls, obj: Dict[str, Any], convert_datetime=True):
        type_hooks = {}
        if convert_datetime:
            type_hooks[datetime] = parse_datetime

        try:
            return dacite.from_dict(data_class=cls, data=obj, config=dacite.config.Config(strict=False,  # type: ignore
                                                                                          cast=[Enum],
                                                                                          type_hooks=type_hooks))
        except MissingValueError as e:
            raise MissingRequiredFieldsError.from_dacite_error(e)
        except UnexpectedDataError as e:
            raise UnexpectedFieldError.from_dacite_error(e)

    def as_dict(self, convert_datetime=True) -> Dict[str, Any]:
        return asdict(self, dict_factory=partial(_custom_dict_factory, convert_datetime))