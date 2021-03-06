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


import asyncio
from typing import Optional

from opendrop.app.model import AppRootModel
from opendrop.mvp import EntryPoint
from .component import app_cs


class App(EntryPoint):
    root_component = app_cs

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._loop = None  # type: Optional[asyncio.AbstractEventLoop]
        self._model = None  # type: Optional[AppRootModel]

    def start(self) -> None:
        from opendrop.vendor import aioglib
        asyncio.set_event_loop_policy(aioglib.GLibEventLoopPolicy())

        self._loop = asyncio.get_event_loop()
        self._model = AppRootModel(loop=self._loop)

        super().start(model=self._model)

        self._loop.run_forever()

    def _do_stop(self) -> None:
        self._loop.stop()
