# Copyright © 2020, Joseph Berry, Rico Tabor (opendrop.dev@gmail.com)
# OpenDrop is released under the GNU GPL License. You are free to
# modify and distribute the code, but always under the same license
# (i.e. you cannot make commercial derivatives).
#
# If you use this software in your research, please cite the following
# journal articles:
#
# J. D. Berry, M. J. Neeson, R. R. Dagastine, D. Y. C. Chan and
# R. F. Tabor, Measurement of surface and interfacial tension using
# pendant drop tensiometry. Journal of Colloid and Interface Science 454
# (2015) 226–237. https://doi.org/10.1016/j.jcis.2015.05.012
#
# E. Huang, T. Denning, A. Skoufis, J. Qi, R. R. Dagastine, R. F. Tabor
# and J. D. Berry, OpenDrop: Open-source software for pendant drop
# tensiometry & contact angle measurements, submitted to the Journal of
# Open Source Software
#
# These citations help us not only to understand who is using and
# developing OpenDrop, and for what purpose, but also to justify
# continued development of this code and other open source resources.
#
# OpenDrop is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this software.  If not, see <https://www.gnu.org/licenses/>.


import math
from enum import Enum
from typing import Optional, Sequence, Callable, Any

from opendrop.app.ift.analysis import IFTDropAnalysis
from opendrop.app.ift.analysis_saver import IFTAnalysisSaverOptions
from opendrop.utility.bindable import VariableBindable, AccessorBindable
from opendrop.utility.bindable.typing import Bindable
from .graphs import GraphsModel
from .individual.model import IndividualModel


class IFTResultsModel:
    class Status(Enum):
        NO_ANALYSES = 0
        FITTING = 1
        FINISHED = 2
        CANCELLED = 3

    def __init__(
            self,
            in_analyses: Bindable[Sequence[IFTDropAnalysis]],
            do_cancel_analyses: Callable[[], Any],
            do_save_analyses: Callable[[IFTAnalysisSaverOptions], Any],
            create_save_options: Callable[[], IFTAnalysisSaverOptions],
            check_if_safe_to_discard: Callable[[], bool],
    ):
        self.bn_analyses = in_analyses

        self._do_cancel_analyses = do_cancel_analyses
        self._do_save_analyses = do_save_analyses
        self._create_save_options = create_save_options
        self._check_if_safe_to_discard = check_if_safe_to_discard

        self.bn_selection = VariableBindable(None)  # type: Bindable[Optional[IFTDropAnalysis]]

        self.individual = IndividualModel(
            in_analyses=self.bn_analyses,
            bind_selection=self.bn_selection,
        )

        self.graphs = GraphsModel(
            in_analyses=self.bn_analyses,
        )

        self._tracked_analyses = []
        self._analysis_untrack_tasks = {}

        self.bn_fitting_status = AccessorBindable(getter=self._get_fitting_status)
        self.bn_analyses_time_start = AccessorBindable(getter=self._get_analyses_time_start)
        self.bn_analyses_time_est_complete = AccessorBindable(getter=self._get_analyses_time_est_complete)
        self.bn_analyses_completion_progress = AccessorBindable(getter=self._get_analyses_completion_progress)

        self.bn_analyses.on_changed.connect(self._hdl_analyses_changed)

    def _hdl_analyses_changed(self) -> None:
        analyses = self.bn_analyses.get()
        tracked_analyses = self._tracked_analyses

        to_track = set(analyses) - set(tracked_analyses)
        for analysis in to_track:
            self._track_analysis(analysis)

        to_untrack = set(tracked_analyses) - set(analyses)
        for analysis in to_untrack:
            self._untrack_analysis(analysis)

    def _track_analysis(self, analysis: IFTDropAnalysis) -> None:
        untrack_tasks = []

        event_connections = [
            analysis.bn_status.on_changed.connect(
                self.bn_fitting_status.poke
            ),
            analysis.bn_is_done.on_changed.connect(
                self.bn_analyses_completion_progress.poke
            ),
            analysis.bn_time_start.on_changed.connect(
                self.bn_analyses_time_start.poke
            ),
            analysis.bn_time_est_complete.on_changed.connect(
                self.bn_analyses_time_est_complete.poke
            )
        ]

        untrack_tasks.extend(
            ec.disconnect
            for ec in event_connections
        )

        self._tracked_analyses.append(analysis)
        self._analysis_untrack_tasks[analysis] = untrack_tasks

        self.bn_fitting_status.poke()
        self.bn_analyses_completion_progress.poke()
        self.bn_analyses_time_start.poke()
        self.bn_analyses_time_est_complete.poke()

    def _untrack_analysis(self, analysis: IFTDropAnalysis) -> None:
        untrack_tasks = self._analysis_untrack_tasks[analysis]
        for task in untrack_tasks:
            task()

        self._tracked_analyses.remove(analysis)
        del self._analysis_untrack_tasks[analysis]

    def _get_fitting_status(self) -> Status:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return self.Status.NO_ANALYSES

        is_cancelled = any(
            analysis.bn_is_cancelled.get()
            for analysis in analyses
        )
        if is_cancelled:
            return self.Status.CANCELLED

        is_finished = all(
            analysis.bn_is_done.get() and not analysis.bn_is_cancelled.get()
            for analysis in analyses
        )
        if is_finished:
            return self.Status.FINISHED

        return self.Status.FITTING

    def _get_analyses_time_start(self) -> float:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return math.nan

        time_start = min(
            analysis.bn_time_start.get()
            for analysis in analyses
        )

        return time_start

    def _get_analyses_time_est_complete(self) -> float:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return math.nan

        time_est_complete = max(
            analysis.bn_time_est_complete.get()
            for analysis in analyses
        )

        return time_est_complete

    def _get_analyses_completion_progress(self) -> float:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return math.nan

        num_completed = len([
            analysis
            for analysis in analyses
            if analysis.bn_is_done.get()
        ])

        completed_fraction = num_completed/len(analyses)

        return completed_fraction

    def calculate_time_elapsed(self) -> float:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return math.nan

        time_elapsed = max(
            analysis.calculate_time_elapsed()
            for analysis in analyses
        )

        return time_elapsed

    def calculate_time_remaining(self) -> float:
        analyses = self.bn_analyses.get()
        if len(analyses) == 0:
            return math.nan

        time_remaining = max(
            analysis.calculate_time_remaining()
            for analysis in analyses
        )

        return time_remaining

    def cancel_analyses(self) -> None:
        self._do_cancel_analyses()

    def save_analyses(self, options: IFTAnalysisSaverOptions) -> None:
        self._do_save_analyses(options)

    def create_save_options(self) -> IFTAnalysisSaverOptions:
        return self._create_save_options()

    @property
    def is_safe_to_discard(self) -> bool:
        return self._check_if_safe_to_discard()
