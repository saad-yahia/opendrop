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


from typing import Optional

import numpy as np
from gi.repository import Gtk

from opendrop.mvp import ComponentSymbol, View, Presenter
from opendrop.utility.bindable.typing import Bindable

residuals_plot_cs = ComponentSymbol()  # type: ComponentSymbol[Gtk.Widget]


@residuals_plot_cs.view()
class ResidualsPlotView(View['ResidualsPlotPresenter', Gtk.Widget]):
    def _do_init(self) -> Gtk.Widget:
        from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
        from matplotlib.figure import Figure

        self._widget = Gtk.Grid()

        figure = Figure(tight_layout=True)

        self._figure_canvas = FigureCanvas(figure)
        self._figure_canvas.props.hexpand = True
        self._figure_canvas.props.vexpand = True
        self._figure_canvas.show()
        self._widget.add(self._figure_canvas)

        self._axes = figure.add_subplot(1, 1, 1)

        # Set tick labels font size
        for item in (*self._axes.get_xticklabels(), *self._axes.get_yticklabels()):
            item.set_fontsize(8)

        self.presenter.view_ready()

        return self._widget

    def set_data(self, residuals: np.ndarray) -> None:
        axes = self._axes
        axes.clear()

        if residuals is None or len(residuals) == 0:
            axes.set_axis_off()
            self._figure_canvas.draw()
            return

        axes.set_axis_on()
        axes.plot(residuals[:, 0], residuals[:, 1], color='#0080ff', marker='o', linestyle='')
        self._figure_canvas.draw()

    def _do_destroy(self) -> None:
        self._widget.destroy()


@residuals_plot_cs.presenter(options=['in_residuals'])
class ResidualsPlotPresenter(Presenter['ResidualsPlotView']):
    def _do_init(
            self,
            in_residuals: Bindable[Optional[np.ndarray]]
    ) -> None:
        self._bn_residuals = in_residuals

        self.__event_connections = []

    def view_ready(self):
        self.__event_connections.extend([
            self._bn_residuals.on_changed.connect(
                self._hdl_residuals_changed
            ),
        ])

        self._hdl_residuals_changed()

    def _hdl_residuals_changed(self) -> None:
        residuals = self._bn_residuals.get()
        self.view.set_data(residuals)

    def _do_destroy(self) -> None:
        for ec in self.__event_connections:
            ec.disconnect()
