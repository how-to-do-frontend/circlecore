import logging

from circleguard.circleguard import Circleguard, set_options
from circleguard.loadable import Check, Replay, ReplayMap, ReplayPath, Map, User, MapUser, ReplayContainer, LoadableContainer, Loadable
from circleguard.enums import Key, Mod, RatelimitWeight
from circleguard.detect import Detect, StealDetect, RelaxDetect, CorrectionDetect
from circleguard.utils import TRACE, ColoredFormatter
from circleguard.loader import Loader
from circleguard.replay_info import ReplayInfo
from circleguard.exceptions import (CircleguardException, InvalidArgumentsException, APIException,
        NoInfoAvailableException, UnknownAPIException, InternalAPIException, InvalidKeyException, RatelimitException,
        InvalidJSONException, ReplayUnavailableException)
from circleguard.version import __version__
from circleguard.result import (Result, InvestigationResult, ComparisonResult,
        RelaxResult, ResultType, CorrectionResult)
from circleguard.span import Span

logging.addLevelName(TRACE, "TRACE")
formatter = ColoredFormatter("[%(threadName)s][%(name)s][%(levelname)s]  %(message)s  (%(filename)s:%(lineno)s)")
handler_stream = logging.StreamHandler()
handler_stream.setFormatter(formatter)
logging.getLogger("circleguard").addHandler(handler_stream)

__all__ = ["Circleguard", "set_options", "Check", "Replay", "ReplayMap", "StealDetect", "RelaxDetect",
           "CorrectionDetect", "ReplayPath", "Detect", "TRACE", "ColoredFormatter", "Loader", "ReplayInfo",
           "__version__", "RatelimitWeight", "Result", "InvestigationResult",
           "ComparisonResult", "RelaxResult", "ResultType",
           "CircleguardException", "InvalidArgumentsException", "Map", "User",
           "APIException", "NoInfoAvailableException", "UnknownAPIException", "InternalAPIException",
           "InvalidKeyException", "RatelimitException", "InvalidJSONException", "ReplayUnavailableException", "Key",
           "Mod", "CorrectionResult", "MapUser", "ReplayContainer", "LoadableContainer", "Loadable", "Span"]
