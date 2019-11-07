from pathlib import Path
import sys
import itertools
import os
from os.path import isfile, join
import logging
from tempfile import TemporaryDirectory

from circleguard.loader import Loader
from circleguard.comparer import Comparer
from circleguard.investigator import Investigator
from circleguard.cacher import Cacher
from circleguard.exceptions import CircleguardException
from circleguard.replay import Check, ReplayMap, ReplayPath, Replay, Map
from circleguard.enums import Detect, RatelimitWeight
from slider import Beatmap, Library


class Circleguard:
    """
    Circleguard investigates replays for cheats.

    Parameters
    ----------
    key: str
        A valid api key. Can be retrieved from https://osu.ppy.sh/p/api/.
    db_path: str or :class:`os.PathLike`
        The path to the database file to read and write cached replays. If the
        given path does not exist, a fresh database will be created there.
        If `None`, no replays will be cached or loaded from cache.
    slider_dir: str or :class:`os.PathLike`
        The path to the directory used by :mod:`slider` to store beatmaps.
        If `None`, a temporary directory will be created for :mod:`slider`,
        and subdsequently destroyed when this :class:`~.circleguard`
        object is garbage collected.
    loader: :class:`~.Loader`
        A :class:`~.Loader` class or subclass, which will be used in place of
        instantiating a new :class:`~.Loader` if passed. This must be the
        class itself, *not* an instantiation of it. It will be instantiated
        upon circleguard instantiation, with two args - a key and a cacher.
    """


    def __init__(self, key, db_path=None, slider_dir=None, loader=None, cache=True):
        self.cache = cache
        self.cacher = None
        if db_path is not None:
            # resolve relative paths
            db_path = Path(db_path).absolute()
            # they can set cache to False later with:func:`~.circleguard.set_options`
            # if they want; assume caching is desired if db path is passed
            self.cacher = Cacher(self.cache, db_path)

        self.log = logging.getLogger(__name__)
        # allow for people to pass their own loader implementation/subclass
        self.loader = Loader(key, cacher=self.cacher) if loader is None else loader(key, self.cacher)
        if slider_dir is None:
            # have to keep a reference to it or the folder gets deleted and can't be walked by Library
            self.slider_dir = TemporaryDirectory()
            # create db and immediately disconnect
            tmp_library = Library.create_db(self.slider_dir.name)
            tmp_library.close()
            self.library = None
        else:
            self.library = Library(slider_dir)


    def run(self, check):
        """
        Investigates replays held in ``container`` for cheats.

        Parameters
        ----------
        container: :class:`~.Container`
            A container holding the replays to investigate.

        Yields
        ------
        :class:`~.Result`
            A result representing a single investigation of the replays
            in ``container``. Depending on how many replays are in
            ``container``, and what type of cheats we are investigating for,
            the total number of :class:`~.Result`\s yielded may vary.

        Notes
        -----
        :class:`~.Result`\s are yielded one at a time, as circleguard finishes
        investigating them. This means that you can process results from
        :meth:`~.run` without waiting for all of the investigations to finish.
        """

        c = check
        self.log.info("Running circleguard with %r", c)

        c.load(self.loader)
        d = c.detect
        # steal check
        if Detect.STEAL in d:
            compare1 = c.all_replays()
            compare2 = c.all_replays2()
            comparer = Comparer(d.steal_thresh, compare1, replays2=compare2)
            yield from comparer.compare()

        # relax check
        if Detect.RELAX in d:
            if self.library is None:
                # connect to library since it's a temporary one
                library = Library(self.slider_dir.name)
            else:
                library = self.library

            for replay in c.all_replays():
                bm = library.lookup_by_id(replay.map_id, download=True, save=True)
                investigator = Investigator(replay, bm, d.ur_thresh)
                yield from investigator.investigate()

            if self.library is None:
                # disconnect from temporary library
                library.close()

    def load(self, loadable):
        """
        Loads the given loadable.

        Parameters
        ----------
        loadable: :class:`~.replay.Loadable`
            The loadable to load.

        Notes
        -----
        This is identical to calling ``loadable.load(cg.loader)``.
        """
        loadable.load(self.loader, self.cache)

    def load_info(self, info_loadable):
        """
        Loads the given info loadable.

        Parameters
        ----------
        loadable: :class:`~.replay.InfoLoadable`
            The info loadable to load.

        Notes
        -----
        This is identical to calling ``info_loadable.load_info(cg.loader)``.
        """
        info_loadable.load_info(self.loader)


    def set_options(self, cache=None):
        """
        Sets options for this instance of circlecore.

        Parameters
        ----------
        cache: bool
            Whether to cache loaded loadables.
        """

        # remnant code from when we had many options available in set_options. Left in for easy future expansion
        for k, v in locals().items():
            if v is None or k == "self":
                continue
            if k == "cache":
                self.cache = cache
                self.cacher.should_cache = cache
                continue

def set_options(loglevel=None):
    """
    Set global options for circlecore.

    Parameters
    ---------
    logevel: int
        What level to log at. Circlecore follows standard python logging
        levels, with an added level of TRACE with a value of 5 (lower than
        debug, which is 10). The value passed to loglevel is passed directly to
        the setLevel function of the circleguard root logger. WARNING by
        default. For more information on log levels, see the standard python
        logging lib.
    """
    if loglevel is not None:
        logging.getLogger("circleguard").setLevel(loglevel)
